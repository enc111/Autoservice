from datetime import datetime, timedelta
from django import forms
from django.core.exceptions import ValidationError
from autosaloons.models import AutosaloonBranch, BranchHall, DinnerWagon
from orders.models import Order


class TableForm(forms.Form):
    address = forms.ChoiceField(
        label='Адрес заведения',
        error_messages={
            'required': 'Поле адреса заведения не может быть пустым'
        },
        required=True
    )
    hall = forms.ChoiceField(
        label='Тип зала заведения',
        error_messages={
            'required': 'Поле типа зала заведения не может быть пустым'
        },
        required=True
    )
    date = forms.DateField(
        label='Дата бронирования',
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'placeholder': 'ДД-ММ-ГГГГ'
            },
        ),
        error_messages={
            'required': 'Поле даты бронирования не может быть пустым',
            'invalid': 'Неверный формат записи даты бронирования'
        },
        required=True
    )
    time = forms.TimeField(
        label='Время бронирования',
        input_formats=['%H:%M'],
        widget=forms.TimeInput(
            attrs={
                'type': 'time',
                'placeholder': 'ЧЧ:ММ'
            },
        ),
        error_messages={
            'required': 'Поле времени бронирования не может быть пустым',
            'invalid': 'Неверный формат записи времени бронирования'
        },
        required=True
    )
    table = forms.ChoiceField(
        label='Количество мест за столиком',
        error_messages={
            'required': 'Поле столика заведения не может быть пустым'
        },
        help_text='Если поле пустое, то свободных столиков нет',
        required=True
    )
    phone = forms.CharField(
        label='Ваш контактный телефон',
        widget=forms.TextInput(attrs={'placeholder': '9004001020'}),
        max_length=10,
        error_messages={
            'required': 'Поле номера телефона не может быть пустым'
        },
        help_text='Необходим для обработки и подтверждения заказа сотрудниками заведения.',
        required=True
    )

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        symbols_list = list(phone)
        if symbols_list.__len__() < 10:
            raise forms.ValidationError('Номер телефона должен состоять из 10 цифр')
        for symbol in symbols_list:
            try:
                int_value = int(symbol)
                if int_value < 0:
                    raise forms.ValidationError('Неверный номер телефона')
            except ValueError:
                raise forms.ValidationError('Неверный номер телефона')
        return phone

    def clean(self):
        order_date = self.cleaned_data.get('date')
        order_time = self.cleaned_data.get('time')
        if order_date is None:
            raise ValidationError('Поле даты бронирования не должо быть пустым')
        elif order_time is None:
            raise ValidationError('Поле времени бронирования не должо быть пустым')
        # TODO учитывать временные зоны (date_time содержит дату с учетом временой зоны) сейчас - абсолютоное время
        execution_date_time = datetime(
            order_date.year,
            order_date.month,
            order_date.day,
            order_time.hour,
            order_time.minute
        )
        date_time_border = datetime.now() + timedelta(hours=2)
        if execution_date_time <= date_time_border:
            error_message = 'Невозможно оформить заказ на выбранное время'
            self.add_error('date', error_message)
            self.add_error('time', error_message)

    def __init__(self, autosaloon_id, branch_id, hall_type, order_date, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if autosaloon_id != -1:
            if AutosaloonBranch.objects.filter(autosaloon__id=autosaloon_id).exists():
                self.fields['address'] = forms.ChoiceField(
                    choices=[(branch.id, branch.address) for branch in AutosaloonBranch.objects.filter(
                        autosaloon__id=autosaloon_id
                    )],
                    label='Адрес заведения',
                    required=True
                )

                if branch_id == -1 and hall_type == -1 and order_date == -1:
                    # загружаем данные формы по умолчанию
                    default_branch = AutosaloonBranch.objects.filter(autosaloon__id=autosaloon_id).first()
                    self.fields['hall'] = forms.ChoiceField(
                        choices=[(hall.type, hall.get_type_display()) for hall in BranchHall.objects.filter(
                            branch=default_branch
                        )],
                        label='Тип зала заведения',
                        error_messages={
                            'required': 'Поле адреса заведения не может быть пустым'
                        },
                        required=True
                    )

                    default_date = datetime.now() + timedelta(days=1)

                    default_hall = BranchHall.objects.filter(branch=default_branch).first()
                    # определяем, какие столики на заданную дату свободны
                    tables_in_hall = DinnerWagon.objects.filter(hall=default_hall)
                    hall_tables_specification = {}
                    for table in tables_in_hall:
                        if hall_tables_specification.get(table.seats) is None:
                            hall_tables_specification[table.seats] = 1
                        else:
                            hall_tables_specification[table.seats] += 1
                    table_orders_for_default_date = Order.objects.filter(
                        execute_date=default_date.date(),
                        type=Order.TYPE_DINNER_WAGON,
                        autosaloon_branch=default_branch,
                        dinner_wagon__hall=default_hall
                    )
                    order_tables_specification = {}
                    for order in table_orders_for_default_date:
                        if order_tables_specification.get(order.dinner_wagon.seats) is None:
                            order_tables_specification[order.dinner_wagon.seats] = 1
                        else:
                            order_tables_specification[order.dinner_wagon.seats] += 1
                    keys_for_delete = []
                    for hall_table_key in hall_tables_specification.keys():
                        if order_tables_specification.get(hall_table_key) is not None:
                            hall_tables_specification[hall_table_key] -= 1
                            if hall_tables_specification[hall_table_key] == 0:
                                keys_for_delete.append(hall_table_key)
                    for key in keys_for_delete:
                        del hall_tables_specification[key]
                    # в результате hall_tables_specification пуст или содержит свободные столики на заданную дату
                    self.fields['table'] = forms.ChoiceField(
                        choices=[(key, key) for key in hall_tables_specification.keys()],
                        error_messages={
                            'required': 'Поле столика заведения не может быть пустым'
                        },
                        help_text='Если поле пустое, то свободных столиков нет',
                        label='Количество мест за столиком',
                        required=True
                    )
                elif branch_id != -1 and hall_type == -1 and order_date == -1:
                    # загрузка формы после изменения выбора филиала заведения
                    default_branch = AutosaloonBranch.objects.filter(
                        autosaloon__id=autosaloon_id,
                        id=branch_id
                    ).first()
                    self.fields['hall'] = forms.ChoiceField(
                        choices=[(hall.type, hall.get_type_display()) for hall in BranchHall.objects.filter(
                            branch=default_branch
                        )],
                        label='Тип зала заведения',
                        required=True
                    )

                    default_date = datetime.now() + timedelta(days=1)

                    default_hall = BranchHall.objects.filter(branch=default_branch).first()
                    # определяем, какие столики на заданную дату свободны
                    tables_in_hall = DinnerWagon.objects.filter(hall=default_hall)
                    hall_tables_specification = {}
                    for table in tables_in_hall:
                        if hall_tables_specification.get(table.seats) is None:
                            hall_tables_specification[table.seats] = 1
                        else:
                            hall_tables_specification[table.seats] += 1
                    table_orders_for_default_date = Order.objects.filter(
                        execute_date=default_date.date(),
                        type=Order.TYPE_DINNER_WAGON,
                        autosaloon_branch=default_branch,
                        dinner_wagon__hall=default_hall
                    )
                    order_tables_specification = {}
                    for order in table_orders_for_default_date:
                        if order_tables_specification.get(order.dinner_wagon.seats) is None:
                            order_tables_specification[order.dinner_wagon.seats] = 1
                        else:
                            order_tables_specification[order.dinner_wagon.seats] += 1
                    keys_for_delete = []
                    for hall_table_key in hall_tables_specification.keys():
                        if order_tables_specification.get(hall_table_key) is not None:
                            hall_tables_specification[hall_table_key] -= 1
                            if hall_tables_specification[hall_table_key] == 0:
                                keys_for_delete.append(hall_table_key)
                    for key in keys_for_delete:
                        del hall_tables_specification[key]
                    # в результате hall_tables_specification пуст или содержит свободные столики на заданную дату
                    self.fields['table'] = forms.ChoiceField(
                        choices=[(key, key) for key in hall_tables_specification.keys()],
                        error_messages={
                            'required': 'Поле столика заведения не может быть пустым'
                        },
                        help_text='Если поле пустое, то свободных столиков нет',
                        label='Количество мест за столиком',
                        required=True
                    )
                elif branch_id != -1 and hall_type != -1 and order_date == -1:
                    # что-то не то с датой бронирования столика
                    default_branch = AutosaloonBranch.objects.filter(
                        autosaloon__id=autosaloon_id,
                        id=branch_id
                    ).first()
                    self.fields['hall'] = forms.ChoiceField(
                        choices=[(hall.type, hall.get_type_display()) for hall in BranchHall.objects.filter(
                            branch=default_branch
                        )],
                        label='Тип зала заведения',
                        required=True
                    )

                    default_date = datetime.now() + timedelta(days=1)

                    default_hall = BranchHall.objects.filter(branch=default_branch).first()
                    # определяем, какие столики на заданную дату свободны
                    tables_in_hall = DinnerWagon.objects.filter(hall=default_hall)
                    hall_tables_specification = {}
                    for table in tables_in_hall:
                        if hall_tables_specification.get(table.seats) is None:
                            hall_tables_specification[table.seats] = 1
                        else:
                            hall_tables_specification[table.seats] += 1
                    table_orders_for_default_date = Order.objects.filter(
                        execute_date=default_date.date(),
                        type=Order.TYPE_DINNER_WAGON,
                        autosaloon_branch=default_branch,
                        dinner_wagon__hall=default_hall
                    )
                    order_tables_specification = {}
                    for order in table_orders_for_default_date:
                        if order_tables_specification.get(order.dinner_wagon.seats) is None:
                            order_tables_specification[order.dinner_wagon.seats] = 1
                        else:
                            order_tables_specification[order.dinner_wagon.seats] += 1
                    keys_for_delete = []
                    for hall_table_key in hall_tables_specification.keys():
                        if order_tables_specification.get(hall_table_key) is not None:
                            hall_tables_specification[hall_table_key] -= 1
                            if hall_tables_specification[hall_table_key] == 0:
                                keys_for_delete.append(hall_table_key)
                    for key in keys_for_delete:
                        del hall_tables_specification[key]
                    # в результате hall_tables_specification пуст или содержит свободные столики на заданную дату
                    self.fields['table'] = forms.ChoiceField(
                        choices=[(key, key) for key in hall_tables_specification.keys()],
                        error_messages={
                            'required': 'Поле столика заведения не может быть пустым'
                        },
                        help_text='Если поле пустое, то свободных столиков нет',
                        label='Количество мест за столиком',
                        required=True
                    )
                else:
                    # загружаем данные формы с полученным данными
                    default_branch = AutosaloonBranch.objects.filter(
                        autosaloon__id=autosaloon_id,
                        id=branch_id
                    ).first()
                    self.fields['hall'] = forms.ChoiceField(
                        choices=[(hall.type, hall.get_type_display()) for hall in BranchHall.objects.filter(
                            branch=default_branch
                        )],
                        label='Тип зала заведения',
                        required=True
                    )

                    default_hall = BranchHall.objects.filter(
                        branch=default_branch,
                        type=hall_type
                    ).first()
                    # определяем, какие столики на заданную дату свободны
                    tables_in_hall = DinnerWagon.objects.filter(hall=default_hall)
                    hall_tables_specification = {}
                    for table in tables_in_hall:
                        if hall_tables_specification.get(table.seats) is None:
                            hall_tables_specification[table.seats] = 1
                        else:
                            hall_tables_specification[table.seats] += 1
                    table_orders_for_default_date = Order.objects.filter(
                        execute_date=order_date,
                        type=Order.TYPE_DINNER_WAGON,
                        autosaloon_branch=default_branch,
                        dinner_wagon__hall=default_hall
                    )
                    order_tables_specification = {}
                    for order in table_orders_for_default_date:
                        if order_tables_specification.get(order.dinner_wagon.seats) is None:
                            order_tables_specification[order.dinner_wagon.seats] = 1
                        else:
                            order_tables_specification[order.dinner_wagon.seats] += 1
                    keys_for_delete = []
                    for hall_table_key in hall_tables_specification.keys():
                        if order_tables_specification.get(hall_table_key) is not None:
                            hall_tables_specification[hall_table_key] -= 1
                            if hall_tables_specification[hall_table_key] == 0:
                                keys_for_delete.append(hall_table_key)
                    for key in keys_for_delete:
                        del hall_tables_specification[key]
                    # в результате hall_tables_specification пуст или содержит свободные столики на заданную дату
                    self.fields['table'] = forms.ChoiceField(
                        choices=[(key, key) for key in hall_tables_specification.keys()],
                        error_messages={
                            'required': 'Поле столика заведения не может быть пустым'
                        },
                        help_text='Если поле пустое, то свободных столиков нет',
                        label='Количество мест за столиком',
                        required=True
                    )


class DeliveryForm(forms.Form):
    date = forms.DateField(
        label='Дата доставки',
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'placeholder': 'ДД-ММ-ГГГГ'
            },
        ),
        error_messages={
            'required': 'Поле даты доставки не может быть пустым',
            'invalid': 'Неверный формат записи даты доставки'
        },
        required=True
    )
    time = forms.TimeField(
        label='Время доставки',
        input_formats=['%H:%M'],
        widget=forms.TimeInput(
            attrs={
                'type': 'time',
                'placeholder': 'ЧЧ:ММ'
            },
        ),
        error_messages={
            'required': 'Поле времени доставки не может быть пустым',
            'invalid': 'Неверный формат записи времени доставки'
        },
        required=True
    )
    address = forms.CharField(
        label='Адрес для доставки',
        widget=forms.TextInput(attrs={'placeholder': 'ул. Врешинина, 39-А'}),
        max_length=50,
        error_messages={
            'required': 'Поле адреса доставки не может быть пустым'
        },
        help_text='Адрес в пределах выбранного города.',
        required=True
    )
    phone = forms.CharField(
        label='Ваш контактный телефон',
        widget=forms.TextInput(attrs={'placeholder': '9004001020'}),
        max_length=10,
        error_messages={
            'required': 'Поле номера телефона не может быть пустым'
        },
        help_text='Необходим для обработки и подтверждения заказа сотрудниками заведения.',
        required=True
    )

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        symbols_list = list(phone)
        if symbols_list.__len__() < 10:
            raise forms.ValidationError('Номер телефона должен состоять из 10 цифр')
        for symbol in symbols_list:
            try:
                int_value = int(symbol)
                if int_value < 0:
                    raise forms.ValidationError('Неверный номер телефона')
            except ValueError:
                raise forms.ValidationError('Неверный номер телефона')
        return phone

    def clean(self):
        order_date = self.cleaned_data.get('date')
        order_time = self.cleaned_data.get('time')
        if order_date is None:
            raise ValidationError('Поле даты доставки не должо быть пустым')
        elif order_time is None:
            raise ValidationError('Поле времени доставки не должо быть пустым')
        # TODO учитывать временные зоны (date_time содержит дату с учетом временой зоны) сейчас - абсолютоное время
        execution_date_time = datetime(
            order_date.year,
            order_date.month,
            order_date.day,
            order_time.hour,
            order_time.minute
        )
        date_time_border = datetime.now() + timedelta(hours=2)
        if execution_date_time <= date_time_border:
            error_message = 'Невозможно оформить заказ на выбранное время'
            self.add_error('date', error_message)
            self.add_error('time', error_message)


class PickUpForm(forms.Form):
    address = forms.ChoiceField(
        label='Адрес заведения',
        error_messages={
            'required': 'Поле адреса заведения не может быть пустым'
        },
        required=True
    )
    date = forms.DateField(
        label='Дата самовывоза',
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'placeholder': 'ДД-ММ-ГГГГ'
            },
        ),
        error_messages={
            'required': 'Поле даты самовывоза не может быть пустым',
            'invalid': 'Неверный формат записи даты самовывоза'
        },
        required=True
    )
    time = forms.TimeField(
        label='Время самовывоза',
        input_formats=['%H:%M'],
        widget=forms.TimeInput(
            attrs={
                'type': 'time',
                'placeholder': 'ЧЧ:ММ'
            },
        ),
        error_messages={
            'required': 'Поле времени самовывоза не может быть пустым',
            'invalid': 'Неверный формат записи времени самовывоза'
        },
        required=True
    )
    phone = forms.CharField(
        label='Ваш контактный телефон',
        widget=forms.TextInput(attrs={'placeholder': '9004001020'}),
        max_length=10,
        error_messages={
            'required': 'Поле номера телефона не может быть пустым'
        },
        help_text='Необходим для обработки и подтверждения заказа сотрудниками заведения.',
        required=True
    )

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        symbols_list = list(phone)
        if symbols_list.__len__() < 10:
            raise forms.ValidationError('Номер телефона должен состоять из 10 цифр')
        for symbol in symbols_list:
            try:
                int_value = int(symbol)
                if int_value < 0:
                    raise forms.ValidationError('Неверный номер телефона')
            except ValueError:
                raise forms.ValidationError('Неверный номер телефона')
        return phone

    def clean(self):
        order_date = self.cleaned_data.get('date')
        order_time = self.cleaned_data.get('time')
        if order_date is None:
            raise ValidationError('Поле даты самовывоза не должо быть пустым')
        elif order_time is None:
            raise ValidationError('Поле времени самовывоза не должо быть пустым')
        # TODO учитывать временные зоны (date_time содержит дату с учетом временой зоны) сейчас - абсолютоное время
        execution_date_time = datetime(
            order_date.year,
            order_date.month,
            order_date.day,
            order_time.hour,
            order_time.minute
        )
        date_time_border = datetime.now() + timedelta(hours=2)
        if execution_date_time <= date_time_border:
            error_message = 'Невозможно оформить заказ на выбранное время'
            self.add_error('date', error_message)
            self.add_error('time', error_message)

    def __init__(self, autosaloon_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if AutosaloonBranch.objects.filter(autosaloon__id=autosaloon_id).exists():
            self.fields['address'] = forms.ChoiceField(
                choices=[(branch.id, branch.address) for branch in AutosaloonBranch.objects.filter(
                    autosaloon__id=autosaloon_id
                )],
                label='Адрес заведения',
                required=True
            )


class UserOrdersForm(forms.Form):
    phone = forms.CharField(
        label='Ваш контактный телефон',
        widget=forms.TextInput(attrs={'placeholder': '9004001020'}),
        max_length=10,
        error_messages={
            'required': 'Поле номера телефона не может быть пустым'
        },
        required=True
    )

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        symbols_list = list(phone)
        if symbols_list.__len__() < 10:
            raise forms.ValidationError('Номер телефона должен состоять из 10 цифр')
        for symbol in symbols_list:
            try:
                int_value = int(symbol)
                if int_value < 0:
                    raise forms.ValidationError('Неверный номер телефона')
            except ValueError:
                raise forms.ValidationError('Неверный номер телефона')
        return phone
