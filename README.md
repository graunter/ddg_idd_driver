
# Драйвер для ДГУ и ВРУ

### Установка

#### Через центральный репозиторий

1. Обновить индекс - ```apt update```
2. Установить драйвер - ```apt install ddg-idd-driver```
3. проверить состояние службы - ```service ddg-idd-driver status```

#### Из оффлайн пакета

```
dpkg -i ddg-idd-driver-<version>-<platfor>.deb
```

### Управление сервисом:
```
service ddg-idd-driver start    - запустить
service ddg-idd-driver stop     - остановить
service ddg-idd-driver restart  - перезапустить
service ddg-idd-driver status   - статус
```

## Основные положения по ДГУ:

1. Для корректной работы драйвера должен быть установлен и сконфигурирован счетчик типа "WB-MAP" или любое другое устройство отправляющее значения измеренного напряжения в формате: 

    `/devices/bDDGf0r0_bDDGf0r0_27_n1_DDG/controls/Urms L1 220.0`

    >тип данных - int/float

2. Сервис `ddg-idd-driver` при старте создает файл: `~/ddg-idd-driver/ddg_states.json`. В нем он хранит все последние состояния устройств и модель. Устройства создаются в этом файле после первого принятого сообщения от счетчика. Если при запуске сервиса файл уже существует, то будут немедленно отправлены все параметры состояния 

3. Формат файла ddg_state.json:

```
{
    "bDDGf0r0_bDDGf0r0_27_n1_DDG": {
        "last_start": "2023-11-22T12:38:02.983035",
        "last_stop": "2023-11-22T10:59:25.873637",
        "active": 1,
        "model": "place DDG model here",
        "is_panel": false
    },
    "bDDGf0r0_bDDGf0r0_27_n2_DDG": {
        "last_start": "2023-11-22T10:59:50.156850",
        "last_stop": "2023-11-22T10:59:54.200919",
        "active": 0,
        "model": "place DDG model here",
        "is_panel": false
    },
    "bDDGf0r0_bDDGf0r0_27_n3_DDG": {
        "last_start": "2023-11-22T12:37:52.723140",
        "last_stop": "2023-11-22T11:55:40.315339",
        "active": 1,
        "model": "place DDG model here",
        "is_panel": false
    }
}
```
`bDDGf0r0_bDDGf0r0_27_n1_DDG` - имя устройства

`last_start` - последний пуск

`last_stop` - последний останов

`active` - 0 - остановлен, 1 - работает

`model` - модель ДГУ. НЕОБХОДИМО ВВЕСТИ ВРУЧНУЮ

`is_panel` - тип панели управления. Изначально берется из конфигурационного файла `/etc/ddg-idd-driver/config.yaml`
            данный параметр может быть отредактирован вручную для отправки на сервер

### Ввод модели и типа ДГУ:

    - Остановить службу: `service ddg-idd-driver stop`
    - Вписать параметры в соответствующее устройство в файле /etc/ddg-idd-driver/ddg_states.json
    - Запустить службу: `service ddg-idd-driver start`

### Передаваемые топики и времена:
```
При старте

/devices/<device_name>/controls/is_panel <boolean>
```

```
По изменению: Urms L1 > VThreshold -> active = 1

/devices/<device_name>/controls/active <1/0>
/devices/<device_name>/controls/stop time <time>
/devices/<device_name>/controls/last start time <time>
```
```
С интервалом 5 мин:

/devices/<device_name>/controls/alive <time>
```
```
С интервалом 120 мин:
/devices/<device_name>/controls/active <1/0>
/devices/<device_name>/controls/alive <time>
/devices/<device_name>/controls/stop time <time>
/devices/<device_name>/controls/last start time <time>
/devices/<device_name>/controls/ddg model <model>
/devices/<device_name>/controls/is_panel <boolean>
```


## Основные положения по ВРУ:

1. Для корректной работы драйвера должен быть установлен и сконфигурирован счетчик типа "WB-MAP" или любое другое устройство отправляющее значения измеренного напряжения и тока по трем фазам, в формате: 

    `/devices/bIDDf0r0_bIDDf0r0_44_n1_IDD/controls/Urms L1 220.0`
    `/devices/bIDDf0r0_bIDDf0r0_44_n1_IDD/controls/Urms L2 220.0`
    `/devices/bIDDf0r0_bIDDf0r0_44_n1_IDD/controls/Urms L3 220.0`
    `/devices/bIDDf0r0_bIDDf0r0_44_n1_IDD/controls/Irms L1 2.0`
    `/devices/bIDDf0r0_bIDDf0r0_44_n1_IDD/controls/Irms L2 2.0`
    `/devices/bIDDf0r0_bIDDf0r0_44_n1_IDD/controls/Irms L3 2.0`

    >тип данных - int/float


2. Сервис `ddg-idd-driver` при старте создает файл ``~/ddg-idd-driver/idd_states.json`. в нем он хранит все последние состояния устройств. Устройства создаются в этом файле после первого принятого сообщения от счетчика. Если при запуске сервиса файл уже существует, то немедленно будут отправлены все параметры состояния. 

3. Формат файла idd_state.json:

```
{
    "bIDDf0r0_bIDDf0r0_44_n1_IDD": {
        "Urms L1":220.0,
        "Urms L2":220.0,
        "Urms L3":220.0,
        "Irms L1":2.0,
        "Irms L2":2.0,
        "Irms L3":2.0,
        "state": "in_work",
        "changed": "2023-11-22T10:59:25.873637",
        "in_work": 1,
        "voltage": 1
    },
    "bIDDf0r0_bIDDf0r0_44_n2_IDD": {
        "Urms L1":220.0,
        "Urms L2":220.0,
        "Urms L3":220.0,
        "Irms L1":0.0,
        "Irms L2":0.0,
        "Irms L3":0.0,
        "state": "reserved",
        "changed": "2023-11-22T10:59:25.873637",
        "in_work": 0,
        "voltage": 1
    },
    "bIDDf0r0_bIDDf0r0_44_n3_IDD": {
        "Urms L1":220.0,
        "Urms L2":220.0,
        "Urms L3":0.0,
        "Irms L1":0.0,
        "Irms L2":0.0,
        "Irms L3":0.0,
        "state": "no_voltage",
        "changed": "2023-11-22T10:59:25.873637",
        "in_work": 0,
        "voltage": 0
    }
}
```

`bIDDf0r0_bIDDf0r0_44_n1_IDD` - имя устройства

`Urms L1 ... Urms L3` - измеренные напряжения на фазах L1...L3

`Irms L1 ... Irms L3` - измеренные токи на фазах L1...L3

`state` - offline - счетчик не передает данные, no_voltage - нет напряжения на одной из фаз, reserved - в резерве, нет потребления, in_work - в работе, есть потребление по всем фазам > 1А

`changed` - дата и время последней сменя состояния

`in_work` - в работе, 0 - нет, 1 - да

`voltage` - напряжение, 0 - отсутствует, 1 - присутствует


### Передаваемые топики и времена:

```
По изменению Urms L1-L3 и Irms L1-L3:

/devices/{deviceName}/controls/state 'offline/no_voltage/working/reserved'
/devices/{deviceName}/controls/changed '{now_time}'   (отправляется по изменению "state")
```

```
С интервалом 120 мин:
/devices/{deviceName}/controls/state 'offline/no_voltage/working/reserved'
/devices/{deviceName}/controls/changed '{now_time}'   (отправляется по изменению "state")
```

### Состояния

#### "offline"

- если в течении минуты не было получено ни одного параметра со счетчика.

#### "no_voltage"

- если хотя бы на одной из фаз напряжение ниже 100В.

#### "reserved"

- на всех фазах напряжение выше 100В и хотя бы на одной фазе ток ниже 1А.

#### "working"

- на всех фазах напряжение выше 100В и на всех фазах ток выше 1А.



## Сборка пакета:

### Для инсталлятора в виде исполняемых файлов

- перейти в папку 'project/scripts'
- запустить скрипт build.sh с параметрами
    - адрес машины для сборки
    - порт для подключения ssh
    - пароль пользователя root

пример:
```
cd project/scripts
./build.sh 192.168.1.100 22 test
```


