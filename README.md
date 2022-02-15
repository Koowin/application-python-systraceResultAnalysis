# application-python-systraceResultAnalysis
Konkuk University, Team project

# 개요

 2021-2학기 건국대학교 졸업 프로젝트로 진행한 안드로이드 성능 변화 분석 툴 중 Systrace Analyzer, Pattern Analyer 파트입니다.

<br>

## 소개

 시스템 프로세스 별 작업량이 Android 성능 변화에 유의미한 영향을 줄 것이라는 가설을 세웠습니다. 다양한 시스템 프로세스 별 작업량을 객관적으로 분석할 수 있는 툴을 개발하고자 합니다. 프로젝트에서 소개한 툴이 Android 개발자에게 앱 성능 향상 분석에 도움을 줄 수 있을 것으로 기대합니다.

 Systrace 는 특정 기간 동안 추적한 결과를 도출합니다. 특정 앱이 점유한 CPU time, Disk I/O 시간, Database 사용 시간 등이 얼마인지 알 수 는 있지만 특정 기간에만 이루어진 결과를 이용해 성능변화를 추측하기에는 무리가 있습니다.

 이를 해결하기 위한 방안으로, 하나의 추적 결과에 대한 전체 추적 시간 중 CPU 점유 시간, Disk I/O 시간, Database 사용 시간 등의 비율을 매번 Amazon DB에 중복 없이 업로드하면 값이 누적될 경우 평균 값에 가까워저 성능변화 추측에 사용할 수 있는 유의미한 값이 도출될 것이라는 합의를 도출해냈습니다.

 BenchMark & UserPattern Application 은 성능 측정과 측정 변화를 관측하고 일정 기간 동안 사용자가 휴대폰에서 사용한 프로세스의 총 누적 실행 시간을 추적합니다.

 SystraceAnalyzer 는 Systrace 추적을 통해 나온 결과를 분석해 각 프로세스별 실행 시간 비율을 측정하여 Amazon DynamoDB 에 업로드 합니다. 이러한 결과들을 시각화하는 기능도 제공합니다.

 Pattern Analyzer 는 위 앱의 프로세스 누적 실행 시간과 DynamoDB 에 업로드 된 평균 값을 이용하여 각 카테고리별 실행 추정 시간을 도출해냅니다.

<br>

## 파트 상세 소개

### **BenchMark & UserPattern Application**

* “BenchMark & UserPattern Application”은 Benchmark 기능과 사용자 패턴 분석 기능을 제공합니다. 
* Benchmark 기능은 sequential read, sequential write, random read, random write 4가지 카테고리별 성능을 측정하여 보여준다. 단일 측정 기록은 history 화면에서 확인할 수 있으며, 카테고리별 성능 변화 추이는 통계 화면에서 그래프 형태로 확인할 수 있습니다. 
* 사용자 패턴 분석 기능은 선택한 기간 동안 사용한 application별 사용 시간과 핸드폰 사용 시간을 보여준다. 분석 결과는 공유 기능을 통해 application의 package name과 사용 시간을 텍스트 파일로 다운 받을 수 있습니다.
* https://github.com/kshhub/BenchMark

<br>

### **Systrace Analyzer**

* CPU Schedule, Disk I/O, Database 3개의 옵션 중 한가지에 대해 분석한 Systrace 결과 파일을 읽어 옵션을 판단하고 분석합니다.
* Case1: Systrace 결과 파일을 분석하여 시각화하고, 결과값을 DynamoDB에 업로드 합니다.Case2: DynamoDB에 누적된 값들의 평균을 불러와 3가지 옵션에 대한 실행 시간 비율을 시각화하여 제공합니다.
* https://github.com/Koowin/application-python-systraceResultAnalysis

<br>

### **Pattern Analyzer**

* Benchmark & UserPattern Application과 연동하여 실행하는 프로그램입니다.
* UserPattern 분석을 한 후 결과 파일을 공유하기 기능을 통해 txt파일로 저장합니다.
* txt 파일에 저장된 Application package name, 실행 시간, DynamoDB에 누적된 실행시간 비율을 이용하여 해당 유저의 CPU, Disk, Database 각각의 옵션에 대한 실행시간 추정값을 구하여 출력합니다.
* https://github.com/Koowin/application-python-systraceResultAnalysis

<br><br>

# Systrace Analyzer

## Systrace란?

 Systrace는 Android 기기 성능을 분석하기 위한 기본 도구입니다. 안드로이드 디바이스를 연결하여 명령어 실행을 통해 옵션으로 준 기간 동안 추적을 할 수 있으며 추적 결과를 html 파일로 출력합니다.

Systrace에 대한 설명은 다음 링크에서 자세하게 확인하실 수 있습니다. [Android 개발자 > 문서 > 가이드 > 시스템 트레이스 캡처](https://developer.android.com/topic/performance/tracing/command-line?hl=ko)

<br>

## 개념도

![img](https://lh3.googleusercontent.com/LOqp5rzMFKV7IdAXnXcYLWgInEjNKxLKqJIq4ysT_UEd3j6JioaIAxpICMEqi7pgOO3WBm1CDDyT6HKlF1d6rFLIBEvjZjmG3x_7lvMkUDpogxbxwMvtOlFcHj6gerR6WMnp56w0)

<br>

## Use Case

![img](https://lh3.googleusercontent.com/Iyqi_fZ05h3oaC6yU9gtswabkUPBmBWFqp5RO2wCFjUkSPkPMcn1bSwEz6SAJs1M9sC3faeG6ofcfB__zqj579T55IhWESsMU29lwmpX8io2NI4VUI3dadsIBlgF6V9s0Q7ezvVc)

![img](https://lh3.googleusercontent.com/74VbOdpTeZEXMtosetda5TdUvcLG7lo-cOGRaa19xuciPeGb_m71TnSYo1LwnrBkGGPLKYFciTlRrc2FzujkBkmwx2POrSGtaatK0WNry2hrpRRpM-VGB1qxs_YiT0Ns9m8Ao4PJ)

![img](https://lh6.googleusercontent.com/bcAtdyEWKpSJUpVU9BVEacky2yGv4dDiKGarwmmRsZOpRqf5odM-92RvxizSQTKzZI21RK2N_TSNckJM-MUu_2zC1d7DNYjbhwR9KxZOk22EVR6pz2nzI9dZ_uSWZ_XDHTy6StsJ)

<br><br>

# Pattern Analyzer

## Use Case

![img](https://lh4.googleusercontent.com/cgTcBCx0CjwqXiIpe1nYdmKQdSpqen0cd--rkJshYD-FAVNmxe3Y9bgMJDxyHuB8bs3cEj9Rbx1-MZehg-Unwto0mJ56Qqbo6ZLMRtA8q02tHQ_aDi9AElTp-qY3S47nYKZq_1dl)
