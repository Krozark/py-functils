    
class BulkCreateQuerySet(QuerySet):
    def bulk_create(self, objs, batch_size=None, ignore_conflicts=False, **kwargs):
        """
        Inserts each of the instances into the database. This does *not* call
        save() on each of the instances, does not send any pre/post save
        signals, and does not set the primary key attribute if it is an
        autoincrement field (except if features.can_return_ids_from_bulk_insert=True).
        Add Multi-table support to the django version (only work with postgres).
        """
        # res = super().bulk_create(objs, batch_size=batch_size, **kwargs)
        # return res

        assert batch_size is None or batch_size > 0

        first_ancestors = collections.OrderedDict()
        parents = collections.OrderedDict()

        def init_parent_dict(_meta):
            for parent, field in _meta.parents.items():
                init_parent_dict(parent._meta)
                if parent._meta.concrete_model is not _meta.concrete_model:
                    d = parents if parent._meta.parents else first_ancestors
                    if parent in d:
                        d[parent].append(field)
                    else:
                        d[parent] = [field]
        init_parent_dict(self.model._meta)
        is_subclassed = bool(first_ancestors) or bool(parents)

        connection = connections[self.db]

        if is_subclassed:
            if not connection.features.can_return_rows_from_bulk_insert:
                raise ValueError("Can't bulk create a multi-table inherited model")
            if len(first_ancestors) > 1:
                raise NotImplemented("Can't bulk create a multi-table inherited model with multiple pk ancestors")
            assert first_ancestors

        if not objs:
            return objs

        self._for_write = True
        opts = self.model._meta
        fields = opts.concrete_fields
        objs = list(objs)
        self._prepare_for_bulk_create(objs)
        with transaction.atomic(using=self.db, savepoint=False):
            objs_with_pk, objs_without_pk = partition(lambda o: o.pk is None, objs)
            if objs_with_pk:
                # block copied from https://github.com/django/django/blob/stable/3.2.x/django/db/models/query.py#L501
                #self._batched_insert(objs_with_pk, fields, batch_size)
                returned_columns = self._batched_insert(objs_with_pk, fields, batch_size, ignore_conflicts=ignore_conflicts)
                for obj_with_pk, results in zip(objs_with_pk, returned_columns):
                    for result, field in zip(results, opts.db_returning_fields):
                        if field != opts.pk:
                            setattr(obj_with_pk, field.attname, result)
                for obj_with_pk in objs_with_pk:
                    obj_with_pk._state.adding = False
                    obj_with_pk._state.db = self.db
            if objs_without_pk:
                if not is_subclassed:
                    # block copied from https://github.com/django/django/blob/stable/3.2.x/django/db/models/query.py#L512
                    fields = [f for f in fields if not isinstance(f, AutoField)]
                    returned_columns = self._batched_insert(objs_without_pk, fields, batch_size, ignore_conflicts=ignore_conflicts)
                    if connection.features.can_return_rows_from_bulk_insert and not ignore_conflicts:
                        assert len(returned_columns) == len(objs_without_pk)
                    for obj_without_pk, results in zip(objs_without_pk, returned_columns):
                        for result, field in zip(results, opts.db_returning_fields):
                            setattr(obj_without_pk, field.attname, result)
                        obj_without_pk._state.adding = False
                        obj_without_pk._state.db = self.db
                else:
                    # bulk create the parents with pk first
                    for parent, ptr_fields in first_ancestors.items():
                        fields = [f for f in parent._meta.local_fields if not isinstance(f, AutoField)]
                        ids = parent.objects.get_queryset()._batched_insert(objs_without_pk, fields, batch_size, ignore_conflicts=ignore_conflicts)
                        assert len(ids) == len(objs_without_pk)
                        for obj, pk in zip(objs_without_pk, ids):
                            # set the obj.pk, created with the parent
                            # only work if pk is unambiguous and points to the same field for parent model and self
                            # for some reason, pk is returned as a tuple
                            if isinstance(pk, (tuple, list)):
                                assert len(pk) == 1
                                pk = pk[0]
                            setattr(obj, parent._meta.pk.attname, pk)
                            # create concrete parent object
                            obj2 = parent(**{f.name: getattr(obj, f.name) for f in parent._meta.concrete_fields})
                            # also update pointer to parent fields
                            for f in ptr_fields:
                                # <parent>_ptr_id fields
                                setattr(obj, f.attname, pk)
                                # TODO warkoround a bug that don't allow use to assign without pk field present in parent
                                setattr(obj2, f.attname, pk)
                                # <parent>_ptr fields
                                setattr(obj, f.name, obj2)

                    # bulk create intermediary parents
                    for parent, ptr_fields in parents.items():
                        # create with local fields
                        fields = parent._meta.local_fields  # no autofields (pk) here
                        parent.objects.get_queryset()._batched_insert(objs_without_pk, fields, batch_size, ignore_conflicts=ignore_conflicts)
                        # update parent_ptr fields
                        for obj in objs_without_pk:
                            obj2 = parent(**{f.name: getattr(obj, f.name) for f in parent._meta.concrete_fields})
                            for f in ptr_fields:
                                setattr(obj, f.name, obj2)
                    fields = self.model._meta.local_fields  # no autofields (pk) here
                    returned_columns = self._batched_insert(objs_without_pk, fields, batch_size, ignore_conflicts=ignore_conflicts)

                    # finalize the objects
                    for obj_without_pk, results in zip(objs_without_pk, returned_columns):
                        for result, field in zip(results, opts.db_returning_fields):
                            setattr(obj_without_pk, field.attname, result)
                        obj_without_pk._state.adding = False
                        obj_without_pk._state.db = self.db
        return objs

