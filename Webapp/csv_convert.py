import pandas as pd

# --- 설정 ---
INPUT_FILE = "C:/Users/euing/Documents/vscode/매형/성장도표+데이터+테이블.csv"
OUTPUT_MALE_FILE = "C:/Users/euing/Documents/vscode/매형/growth_data_male.csv"
OUTPUT_FEMALE_FILE = "C:/Users/euing/Documents/vscode/매형/growth_data_female.csv"

# --- 1. 파일 읽기 ---
try:
    # 한국어 인코딩(cp949)과 헤더 없음(None)으로 파일 읽기 시도
    df = pd.read_csv(INPUT_FILE, header=None, encoding='cp949')
except UnicodeDecodeError:
    try:
        # cp949 실패 시 euc-kr로 재시도
        df = pd.read_csv(INPUT_FILE, header=None, encoding='euc-kr')
    except Exception as e:
        print(f"ERROR: 파일 읽기 실패. 인코딩 문제 또는 파일 경로 오류: {e}")
        exit()
except FileNotFoundError:
    print(f"ERROR: 파일을 찾을 수 없습니다. '{INPUT_FILE}' 파일이 현재 스크립트 위치에 있는지 확인해주세요.")
    exit()

print(f"'{INPUT_FILE}' 파일 읽기 성공.")

# --- 2. 데이터 전처리 및 컬럼 추출 ---
# 원본 CSV의 복잡한 구조를 파악하여 컬럼명 재지정
new_columns = [
    'Sex', 'Age_Years', 'Age_Months', 'L', 'M', 'S', 
    'P1', 'P3', 'P5', 'P10', 'P15', 'P25', 'P50', 'P75', 'P85', 'P90', 'P95', 'P97', 'P99', 
    'Z-3', 'Z-2', 'Z-1', 'Z0', 'Z+1', 'Z+2', 'Z+3'
]
df.columns = new_columns
df_data = df.iloc[2:].copy()

# 필요한 컬럼만 숫자로 변환
cols_to_num = ['Sex', 'Age_Years', 'P3', 'P50', 'P97']
for col in cols_to_num:
    df_data[col] = pd.to_numeric(df_data[col], errors='coerce')

# 만나이(세) 데이터가 있는 행만 필터링 (월령 데이터는 무시하고 연간 데이터만 사용)
df_years = df_data[df_data['Age_Years'].notna()].copy()

# 최종 데이터셋 준비
df_male = df_years[df_years['Sex'] == 1].dropna(subset=cols_to_num)[['Age_Years', 'P3', 'P50', 'P97']]
df_female = df_years[df_years['Sex'] == 2].dropna(subset=cols_to_num)[['Age_Years', 'P3', 'P50', 'P97']]


# --- 3. 새 파일로 저장 ---

# 남자 데이터 저장 (UTF-8 인코딩 사용, 인덱스 및 헤더 제외)
df_male.to_csv(OUTPUT_MALE_FILE, index=False, header=False, encoding='utf-8')

# 여자 데이터 저장 (UTF-8 인코딩 사용, 인덱스 및 헤더 제외)
df_female.to_csv(OUTPUT_FEMALE_FILE, index=False, header=False, encoding='utf-8')

print("\n--- 저장 결과 ---")
print(f"1. 남자 데이터: '{OUTPUT_MALE_FILE}' 파일 저장 완료. ({len(df_male)}개 행)")
print(f"2. 여자 데이터: '{OUTPUT_FEMALE_FILE}' 파일 저장 완료. ({len(df_female)}개 행)")
print("이제 이 두 파일을 Firebase public 폴더에 업로드하세요.")