import os
import redis
from app import create_app, db
from app.models import Collection
from datetime import date, datetime
from shutil import copyfile
from flask_uploads import UploadSet


app = create_app('default')
app_context = app.app_context()
app_context.push()
r = redis.StrictRedis()


def add_timestamp(file_name):
    now = datetime.now()
    time_str = now.strftime("%Y%m%d-%H%M%S")
    return file_name + '-' + time_str


def get_filename(directory):
    files = os.listdir(directory)
    for filename in files:
        yield filename


def extension_allowed(extension):
    return extension in ["jpg", "gif", "jpeg"]


def validate(filename):
    return "." in filename and extension_allowed(filename.split(".")[1].strip())


def parse(filename):
    if validate(filename):
        extension = filename.split(".")[1].strip()
        return extension
    else:
        return None






def insert():
    source = r"D:\App\PotPlayer\Capture"
    destination = r"D:\web\flasky\app\static\img"
    files = os.listdir(source)
    for filename in files:
        if "." in filename:
            extension = filename.split(".")[1].strip()
            if extension in ['jpg']:
                raw_word = filename.split(".")[0].strip()
                word = "word:" + raw_word
                if not r.exists(word):
                    print(word + " no found")
                else:
                    # add timestamp
                    img_file_name = add_timestamp(raw_word)+"."+extension

                    # copy img file
                    copyfile(os.path.join(source, filename), os.path.join(destination, img_file_name))

                    # insert img path into redis
                    img_num = 0
                    while r.hexists(word, "img_"+str(img_num)):
                        img_num += 1
                    r.hset(word, "img_"+str(img_num), "/static/img/"+img_file_name)

                    # insert word into database
                    collection = Collection(
                        name=raw_word,
                        collect_time=date.today()
                    )
                    db.session.add(collection)
                    try:
                        db.session.commit()
                    except:
                        db.session.rollback()
                    print(word + " insert into database successfully")

    os.system(r"del D:\App\PotPlayer\Capture\* /q")


if __name__ == "__main__":
    insert()
