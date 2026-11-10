import uuid

class Category:
    def __init__(self, name, slug, image, active=True):
        self.id = str(uuid.uuid4())
        self.name = name
        self.slug = slug
        self.image = image
        self.active = active