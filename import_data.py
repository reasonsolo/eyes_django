import os
import django
from django.conf import settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eyes1000.settings")
django.setup()
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from pet.models import PetLost, PetFound, PetMaterial, PET_TYPE, GENDER_CHOICE
from wx_auth.models import User
from PIL import Image, ImageOps
from datetime import datetime
import sys
import io
import uuid

GENDER = {
  'GG': GENDER_CHOICE[1][0],
  'MM': GENDER_CHOICE[2][0],
}

PET = {
  'cat': PET_TYPE[1][0],
  'dog': PET_TYPE[2][0],
}

MATERIAL_DIR = 'import'

def Usage():
  print("%s [csv file] [lost|found] [cat|dog]" % sys.argv[0])

def get_mediacal_status(status):
  return ','.join([str(i+1) for i, ch in enumerate(status) if ch == 'Y'])

def get_found_status(status):
  return ','.join([str(i) for i, ch in enumerate(status) if ch == 'Y'])

def get_user():
  return User.objects.filter(wx_openid__isnull=False, wx_nickname__isnull=False, wx_avatar__isnull=False).order_by('?').first()

def store_material(img_path, user):
  print('save img %s' % img_path)
  with open(img_path, 'rb') as img_file:
    img_file = File(img_file)
    fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'material'),
                            base_url=settings.MEDIA_URL + 'material')
    material_dir = os.path.join(settings.MEDIA_ROOT, 'material')
    filename = str(uuid.uuid1()) + '.' + img_path.split('.')[-1]
    filepath = fs.save(filename, img_file)
    upload_url =  fs.url(filepath)

    image = Image.open(img_file)
    image = image.convert('RGB')
    thumb = ImageOps.fit(image, settings.THUMB_SIZE, Image.ANTIALIAS)

    thumb_io = io.BytesIO()
    thumb.save(thumb_io, 'JPEG')
    thumb_io.seek(0)
    thumb_filename = 'thumb_' + filename
    thumb_filepath = fs.save(thumb_filename, thumb_io)
    thumb_url = fs.url(thumb_filepath)
    material = PetMaterial(publisher=user, mime_type='image/jpg', size=img_file.size, url=upload_url, thumb_url=thumb_url)
    material.save()
    return material

def insert_lost(data, pet_type):
  user = get_user()
  lost = PetLost(publisher=user,
                 nickname=data[2],
                 pet_type=PET[pet_type],
                 birthday=datetime.strptime(data[4], "%m/%d/%Y"),
                 gender=GENDER[data[5]],
                 medical_status=get_mediacal_status(data[6:9]),
                 found_time=datetime.strptime(data[9], "%m/%d/%Y"),
                 place=data[10],
                 reward=int(data[11]),
                 description=data[13],
                 latitude=31.2297,
                 longitude=121.4762,
                 )
  lost.save()
  material_dir = os.path.join(MATERIAL_DIR, data[12][1:])
  for img_file in os.listdir(material_dir):
    material = store_material(os.path.join(material_dir, img_file), user)
    material.lost = lost
    material.save()
  print("insert lost %d" % lost.id)
  return lost

def insert_found(data, pet_type):
  user = get_user()
  found = PetFound(publisher=user,
                  pet_type=PET[pet_type],
                  found_time=datetime.strptime(data[5], "%m/%d/%Y"),
                  gender=GENDER[data[8]],
                  found_status=get_found_status(data[2:6]),
                  place=data[6],
                  description=data[10],
                  latitude=31.2297,
                  longitude=121.4762,
                 )
  found.save()
  material_dir = os.path.join(MATERIAL_DIR, data[9][1:])
  for img_file in os.listdir(material_dir):
    material = store_material(os.path.join(material_dir, img_file), user)
    material.found =found 
    material.save()
  print("insert lost %d" % found.id)
  return found 


if __name__ == "__main__":
  if len(sys.argv) < 4:
    Usage()
    sys.exit()
  file_path = sys.argv[1]
  post_type = sys.argv[2]
  pet_type = sys.argv[3]

  if pet_type not in ('cat', 'dog') or post_type not in ['lost', 'found']:
    Usage()
    sys.exit()
  
  with open(file_path) as csv:
    for line in csv:
      data = line.split('\t')
      if post_type == 'lost':
        insert_lost(data, pet_type)
      else:
        insert_found(data, pet_type)

