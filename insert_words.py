import os
import redis
from app import create_app, db
from app.models import Collection
from datetime import date, datetime
from shutil import copyfile
from flask_uploads import UploadSet
from .search import Subtitle


app = create_app('default')
app_context = app.app_context()
app_context.push()
r = redis.StrictRedis()


class FileNameNotValid(Exception):
    """
    This exception is raised if the upload was not allowed. You should catch
    it in your view code and display an appropriate message to the user.
    """


class WordNotFoundInRedis(Exception):
    """
    This exception is raised if the word was not found in redis dictionary. You should catch
    it in your view code and display an appropriate message to the user.
    """


def add_timestamp(file_name):
    now = datetime.now()
    time_str = now.strftime("%Y%m%d-%H%M%S")
    return file_name + '-' + time_str


def list_files(directory):
    files = os.listdir(directory)
    for filename in files:
        yield filename


def extension_allowed(extension):
    return extension in ["jpg", "gif", "jpeg"]


def validate(filename):
    return "." in filename and extension_allowed(filename.split(".")[1].strip())


def parse(filename):
    if validate(filename):
        word = filename.split(".")[0].strip()
        extension = filename.split(".")[1].strip()
        return word, extension
    else:
        raise FileNameNotValid


def format_filename(word, extension):
    return add_timestamp(word) + "." + extension


def insert_into_redis(raw_word, img_file_name):
    word = "word:" + raw_word
    if not r.exists(word):
        raise WordNotFoundInRedis("{} no found".format(word))
    else:
        # insert img path into redis
        img_num = 0
        while r.hexists(word, "img_" + str(img_num)):
            img_num += 1
        r.hset(word, "img_" + str(img_num), "/static/img/" + img_file_name)


def insert_into_db(word):
    subtitle = Subtitle(filename="")
    sentence = subtitle.get_word_sentence(word)
    collection = Collection(
        name=word,
        collect_time=date.today(),
        full_sentence=sentence
    )
    db.session.add(collection)
    try:
        db.session.commit()
    except:
        db.session.rollback()


def insert_all():
    source = r"D:\App\PotPlayer\Capture"
    destination = r"D:\web\flasky\app\static\img"
    for filename in list_files(source):
        try:
            word, extension = parse(filename)
            img_file_name = format_filename(word, extension)
            insert_into_redis(word, img_file_name)

            # copy img file
            copyfile(os.path.join(source, filename), os.path.join(destination, img_file_name))

            insert_into_db(word)
            print("word:{} insert into database successfully".format(word))

        except FileNameNotValid:
            print("filename not validate")
        except WordNotFoundInRedis as e:
            print(e)
    os.system(r"del D:\App\PotPlayer\Capture\* /q")

if __name__ == "__main__":
    insert_all()

