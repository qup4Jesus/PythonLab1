from flask import Flask, render_template, request, url_for
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, IntegerField
from wtforms.validators import NumberRange, DataRequired
from flask_wtf.file import FileField, FileRequired, FileAllowed
from PIL import Image
import numpy as np
import os
import base64
from io import BytesIO
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

os.makedirs('static', exist_ok=True)

class ImageForm(FlaskForm):
    """Форма для загрузки изображения и параметров преобразования"""
    image = FileField('Выберите изображение', validators=[
        FileRequired(message="Пожалуйста, выберите файл"),
        FileAllowed(['jpg', 'png', 'jpeg', 'bmp'], 'Только изображения!')
    ])

    direction = SelectField('Направление', choices=[
        ('vertical', 'По вертикали'),
        ('horizontal', 'По горизонтали')
    ], default='vertical')

    strip_width = IntegerField('Ширина полосы (в пикселях)',
                               validators=[
                                   DataRequired(),
                                   NumberRange(min=1, max=200, message="От 1 до 200")
                               ],
                               default=20)

    submit = SubmitField('Применить')


def swap_strips_vertical(img_array, strip_width):
    """
    Обмен местами чередующихся вертикальных полос

    Параметры:
    - img_array: numpy массив изображения (H, W, 3) или (H, W)
    - strip_width: ширина полосы в пикселях

    Возвращает: новый массив с обменёнными полосами
    """
    height, width = img_array.shape[:2]
    result = img_array.copy()

    # Количество полос
    num_strips = width // strip_width

    for i in range(0, num_strips, 2):
        if i + 1 < num_strips:
            # Вычисляем границы полос
            start1 = i * strip_width
            end1 = (i + 1) * strip_width
            start2 = (i + 1) * strip_width
            end2 = (i + 2) * strip_width

            # Меняем полосы местами
            result[:, start1:end1] = img_array[:, start2:end2]
            result[:, start2:end2] = img_array[:, start1:end1]

    return result


def swap_strips_horizontal(img_array, strip_width):
    """
    Обмен местами чередующихся горизонтальных полос

    Параметры:
    - img_array: numpy массив изображения (H, W, 3) или (H, W)
    - strip_width: ширина полосы в пикселях

    Возвращает: новый массив с обменёнными полосами
    """
    height, width = img_array.shape[:2]
    result = img_array.copy()

    # Количество полос
    num_strips = height // strip_width

    for i in range(0, num_strips, 2):
        if i + 1 < num_strips:
            # Вычисляем границы полос
            start1 = i * strip_width
            end1 = (i + 1) * strip_width
            start2 = (i + 1) * strip_width
            end2 = (i + 2) * strip_width

            # Меняем полосы местами
            result[start1:end1, :] = img_array[start2:end2, :]
            result[start2:end2, :] = img_array[start1:end1, :]

    return result


def create_color_histogram(img_array, title):
    """
    Создаёт гистограмму распределения цветов (R, G, B)
    Возвращает base64 строку для вставки в HTML
    """
    plt.figure(figsize=(10, 5))

    # Если изображение цветное (3 канала)
    if len(img_array.shape) == 3:
        colors = ('r', 'g', 'b')
        labels = ('Красный', 'Зелёный', 'Синий')
        for i, (color, label) in enumerate(zip(colors, labels)):
            hist = plt.hist(img_array[:, :, i].ravel(), bins=50,
                            range=(0, 256), color=color, alpha=0.5, label=label)
    else:
        # Если уже серое
        plt.hist(img_array.ravel(), bins=50, range=(0, 256),
                 color='gray', alpha=0.7, label='Яркость')

    plt.title(title)
    plt.xlabel('Интенсивность пикселя (0-255)')
    plt.ylabel('Количество пикселей')
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Сохраняем в BytesIO
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    buf.seek(0)
    plt.close()

    # Преобразуем в base64
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return f'data:image/png;base64,{img_base64}'


@app.route("/", methods=['GET', 'POST'])
def index():
    form = ImageForm()
    original_url = None
    result_url = None
    histogram = None

    if form.validate_on_submit():
        file = form.image.data
        direction = form.direction.data
        strip_width = form.strip_width.data

        filename = file.filename
        original_path = os.path.join('static', 'original_' + filename)
        result_path = os.path.join('static', 'result_' + filename)

        # Сохраняем оригинал
        file.save(original_path)

        # Открываем изображение
        img = Image.open(original_path)
        img_array = np.array(img)

        # Применяем преобразование в зависимости от направления
        if direction == 'vertical':
            result_array = swap_strips_vertical(img_array, strip_width)
        else:
            result_array = swap_strips_horizontal(img_array, strip_width)

        # Сохраняем результат
        result_img = Image.fromarray(result_array)
        result_img.save(result_path)

        # Создаём гистограмму для исходного изображения
        histogram = create_color_histogram(img_array, 'Распределение цветов исходного изображения')

        original_url = url_for('static', filename='original_' + filename)
        result_url = url_for('static', filename='result_' + filename)

    return render_template('index.html',
                           form=form,
                           original=original_url,
                           result=result_url,
                           histogram=histogram)


if __name__ == "__main__":
    app.run(debug=True)