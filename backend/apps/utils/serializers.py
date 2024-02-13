from rest_framework.serializers import ModelSerializer, Serializer, DateField
from django.db.transaction import atomic


class DateTimeRnageSerializer(Serializer):
    created_at_range_before = DateField(required=False)
    created_at_range_after = DateField(required=False)


class BulkCreateSerializer(ModelSerializer):
    """
        Usage example:        
            class Meta:
                bulky_fields = {
                    "chapter_set" : {
                        "model" : Child,
                        "parent_field_name" : "parent"
                    }
                }
    """

    def extract_bulky_data(self, validated_data : dict):
        bulky_fields_names = self.bulky_fields.keys()
        bulky_data = {}

        for field in bulky_fields_names:
            bulky_data[field] = validated_data.pop(field, [])
        return validated_data, bulky_data

    @atomic    
    def create(self, validated_data):
        validated_data, bulky_data = self.extract_bulky_data(validated_data)
        self.object = super().create(validated_data)
        self.bulk_create(bulky_data)
        return self.object

    def get_parent_extra_data(self, name):
        return {self.bulky_fields[name]['parent_field_name'] : self.object}

    def is_field_fk(self, name):
        return not self.bulky_fields[name].get('is_m2m', False)

    def bulk_create(self, bulky_data:dict):
        for name in self.bulky_fields.keys():
            if self.is_field_fk(name):
                self.bulk_fk_create(
                    self.bulky_fields[name]['model'], 
                    bulky_data[name],
                    **self.bulky_fields[name].get('extra_data', {}),
                    **self.get_parent_extra_data(name)
                )

            else:
              self.bulk_m2m_create(
                    self.bulky_fields[name]['model'], 
                    bulky_data[name],
                    **self.bulky_fields[name].get('extra_data', {}),
              )                  

    def bulk_m2m_create(self, model, data_list:list[dict], **extra_data):
        if not data_list: return
        objects = model.objects.bulk_create([model(**data, **extra_data) for data in data_list])
        m2m_field = getattr(self.objects, "")
        m2m_field.add(objects)

    @property
    def bulky_fields(self):
        return getattr(self.Meta, 'bulky_fields', {})

    def bulk_fk_create(self, model, data_list:list[dict], **extra_data):
        if not data_list:
            return
        return model.objects.bulk_create([model(**data, **extra_data) for data in data_list])