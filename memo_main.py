from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget

from memo_app import app
from memo_data import *
from memo_main_layout import *
from memo_card_layout import *
from memo_edit_layout import txt_Question, txt_Answer, txt_Wrong1, txt_Wrong2, txt_Wrong3

# Константи
main_width, main_height = 1000, 450 # початкові розміри головного вікна
card_width, card_height = 600, 500  # початкові розміри вікна "картка"
time_unit = 1000 # стільки триває одна одиниця часу з тих, на які потрібно засинати
# (у робочій версії програми збільшити в 60 разів!)

# Глобальні змінні
questions_listmodel = QuestionListModel() # список запитань
frm_edit = QuestionEdit(0, txt_Question, txt_Answer, txt_Wrong1, txt_Wrong2, txt_Wrong3) # запам'ятовуємо, що у формі редагування питання з чим пов'язано
radio_list = [rbtn_1, rbtn_2, rbtn_3, rbtn_4]   # список віджетів, який треба перемішувати (для випадкового розміщення відповідей)
frm_card = 0            # тут буде зв'язуватися питання з формою тесту
timer = QTimer()        # таймер для можливості "заснути" на час і прокинутися
win_card = QWidget()    # вікно картки
win_main = QWidget()    # вікно редагування запитань, основне в програмі

# Тестові данні
def testlist():
    frm = Question('Яблуко', 'apple', 'application', 'pinapple', 'apply')
    questions_listmodel.form_list.append(frm)
    frm = Question('Дім', 'house', 'horse', 'hurry', 'hour')
    questions_listmodel.form_list.append(frm)
    frm = Question('Мишка', 'mouse', 'mouth', 'muse', 'museum')
    questions_listmodel.form_list.append(frm)
    frm = Question('Число', 'number', 'digit', 'amount', 'summary')
    questions_listmodel.form_list.append(frm)

# Функції для проведення тесту
def set_card():
    # задає, який вигляд має вікно картки
    win_card.resize(card_width, card_height)
    win_card.move(300, 300)
    win_card.setWindowTitle('Memory Card')
    win_card.setLayout(layout_card)

def sleep_card():
    # картка ховається на час, зазначений у таймері
    win_card.hide()
    timer.setInterval(time_unit * box_Minutes.value() )
    timer.start()

def show_card():
    # показує вікно (за таймером), таймер зупиняється
    win_card.show()
    timer.stop()

def show_random():
    #показати випадкове запитання
    global frm_card # ніби властивість вікна - поточна форма з даними картки
    
    # отримуємо випадкові дані, і випадково ж розподіляємо варіанти відповідей за радіокнопками:
    frm_card = random_AnswerCheck(questions_listmodel, lb_Question, radio_list, lb_Correct, lb_Result)
    
    # ми будемо запускати функцію, коли вікно вже є. Тож показуємо:
    frm_card.show() # завантажити потрібні дані у відповідні віджети
    show_question() # показати на формі панель запитань

def click_OK():
    # перевіряє запитання або завантажує нове запитання
    if btn_OK.text() != 'Наступне питання':
        frm_card.check()
        show_result()
    else:
        # напис на кнопці дорівнює 'Наступний', ось і створюємо наступне випадкове запитання:
        show_random()

def back_to_menu():
    # повернення з тесту у вікно редактора
    win_card.hide()
    win_main.showNormal()

# Функції для редагування питань
def set_main():
    # задає, який вигляд має основне вікно
    win_main.resize(main_width, main_height)
    win_main.move(100, 100)
    win_main.setWindowTitle('Список питань')
    win_main.setLayout(layout_main)

def edit_question(index):
    # завантажує у форму редагування запитання і відповіді, що відповідають переданому рядку
    # index - це об'єкт класу QModelIndex, див. потрібні методи нижче
    if index.isValid():
        i = index.row()
        frm = questions_listmodel.form_list[i]
        frm_edit.change(frm)
        frm_edit.show()

def add_form():
    # додає нове запитання і пропонує його змінити
    questions_listmodel.insertRows()            # Нове питання з'явилося в даних і автоматично в списку на екрані
    last = questions_listmodel.rowCount(0) - 1  # Нове питання - останнє у списку. Знайдемо його позицію.
    # У rowCount передаємо 0, щоб відповідати вимогам функції:
    # цей параметр все одно не використовується, але
    # потрібен за стандартом бібліотеки (метод із параметром index викликається під час відтворення списку)
    index = questions_listmodel.index(last)     # отримуємо об'єкт класу QModelIndex, який відповідає останньому елементу в даних
    list_questions.setCurrentIndex(index)       # робимо відповідний рядок списку на екрані поточним
    edit_question(index)                        # це питання треба довантажити у форму редагування
    # кліка мишкою у нас тут немає, викличемо потрібну функцію з програми
    txt_Question.setFocus(Qt.TabFocusReason)  # переводимо фокус на поле редагування питання, щоб одразу прибиралися "болванки"
    # Qt.TabFocusReason переводить фокус так, як якби було натиснуто клавішу "tab"
    # це зручно тим, що виділяє "болванку", її легко відразу прибрати

def del_form():
    # видаляє питання і перемикає фокус
    questions_listmodel.removeRows(list_questions.currentIndex().row())
    edit_question(list_questions.currentIndex())

def start_test():
    # на початку тесту форма зв'язується з випадковим питанням і показується
    show_random()
    win_card.show()
    win_main.showMinimized()

# Встановлення потрібних з`єднань
def connects():
    list_questions.setModel(questions_listmodel)    # зв'язати список на екрані зі списком запитань
    list_questions.clicked.connect(edit_question)   # під час натискання на елемент списку відкриватиметься для редагування потрібне запитання
    btn_add.clicked.connect(add_form)               # з'єднали натискання кнопки "нове питання" з функцією додавання
    btn_delete.clicked.connect(del_form)            # з'єднали натискання кнопки "видалити питання" з функцією видалення
    btn_start.clicked.connect(start_test)           # натискання кнопки "почати тест"
    btn_OK.clicked.connect(click_OK)                # натискання кнопки "OK" на формі тесту
    btn_Menu.clicked.connect(back_to_menu)          # натискання кнопки "Меню" для повернення з форми тесту в редактор запитань
    timer.timeout.connect(show_card)                # показуємо форму тесту після закінчення таймера
    btn_Sleep.clicked.connect(sleep_card)           # натискання кнопки "спати" у картки-тесту

# Запуск програми
# Основний алгоритм іноді оформляють у функцію, яка запускається, тільки якщо код виконується з цього файлу,
# а не при підключенні як модуль. Дітям це абсолютно не потрібно.
testlist()
set_card()
set_main()
connects()
win_main.show()
app.exec_()