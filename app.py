import streamlit as st
import requests

# إعدادات الصفحة
st.set_page_config(page_title="منصة ذكاء الأعمال الذكية", page_icon="📊", layout="wide")

# تصميم الواجهة
st.title("📊 منصة ذكاء الأعمال (AI BI Platform)")
st.markdown("اسأل أي سؤال عن بيانات الطلبات، وسيقوم الذكاء الاصطناعي بتحليل سجلات قاعدة بيانات Supabase وكتابة تقرير لك.")

# مربع إدخال السؤال
question = st.text_input("ماذا تريد أن تعرف عن البيانات اليوم؟", placeholder="مثال: ما هو إجمالي الطلبات حسب حالة الدفع؟")

if st.button("تحليل البيانات 🚀"):
    if question.strip():
        # إظهار علامة تحميل أثناء تفكير النظام
        with st.spinner("🤖 جاري كتابة الاستعلام، تصفية السجلات من Supabase، وصياغة التقرير..."):
            try:
                # الاتصال بخادم FastAPI الذي بنيناه
                response = requests.post(
                    "http://127.0.0.1:8000/bi-agent/ask",
                    json={"question": question, "session_id": "web-ui", "user_id": "nader-admin"},
                    timeout=600 # ننتظر حتى ينتهي التحليل
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("success"):
                        st.success("✅ اكتمل التحليل بنجاح!")
                        
                        # عرض التقرير بشكل جميل
                        st.markdown("---")
                        st.markdown(data.get("final_report", ""))
                        
                        # عرض الكود خلف الكواليس للمهندسين
                        with st.expander("🛠️ كيف قام الذكاء الاصطناعي بحسابها؟ (تفاصيل استعلام SQL)"):
                            # تم تعديل اللغة هنا إلى sql لتناسب Supabase (PostgreSQL)
                            st.code(data.get("sql_used", ""), language="sql")
                            st.info(f"تم تجميع البيانات في {data.get('raw_data_count', 0)} صفوف نهائية.")
                    else:
                        st.error("حدث خطأ أثناء معالجة البيانات.")
                        st.json(data.get("errors", {}))
                else:
                    st.error(f"خطأ في الاتصال بالخادم: {response.status_code}")
            except requests.exceptions.RequestException as e:
                st.error(f"تعذر الاتصال بخادم FastAPI. تأكد من تشغيل الباك اند. التفاصيل: {e}")
    else:
        st.warning("الرجاء كتابة سؤال أولاً.")