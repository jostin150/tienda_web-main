import uuid

class Address:
    def __init__(self, user_id, address, city, apartment_number=None,
                 tag=None, reference_place=None, receiver_name=None, phone_number=None):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.address = address
        self.city = city
        self.apartment_number = apartment_number
        self.tag = tag
        self.reference_place = reference_place
        self.receiver_name = receiver_name
        self.phone_number = phone_number

    def add_address(self, user):
        if self.user_id != user.id:
            raise ValueError("La dirección no pertenece al usuario")
        if self not in user.addresses:
            user.addresses.append(self)