import streamlit as st
import html
from dotenv import load_dotenv
import os
from gmail_agent import gmail_authenticate, list_inbox, search_emails, read_email, send_email
from product_search import search_amazon_products, search_walmart_products

# ---------------- ENV SETUP ----------------
load_dotenv()
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

# ---------------- APP SETUP ----------------
st.set_page_config(
    page_title="📧 Gmail + Product Search Dashboard",
    page_icon="📩",
    layout="wide"
)
st.title("📧 Gmail + 🛍️ Product Search Dashboard")

# ---------------- GMAIL AUTH ----------------
service = gmail_authenticate()

# ---------------- TABS ----------------
tabs = st.tabs([
    "📥 Inbox",
    "🔍 Search Emails",
    "✉️ Send Email",
    "🛒 Amazon Product Search",
    "🏬 Walmart Product Search"
])

# =====================================================
# 📥 INBOX TAB
# =====================================================
with tabs[0]:
    st.subheader("📥 Inbox - View Recent Emails")
    col1, col2 = st.columns([1, 2])
    with col1:
        num_emails = st.slider("Number of emails to show:", 5, 30, 10)
    with col2:
        unread_only = st.checkbox("Show unread only")

    if st.button("🔄 Refresh Inbox"):
        emails = list_inbox(service, num_emails)
        if not emails:
            st.info("No emails found.")
        else:
            for e in emails:
                if unread_only and not e['unread']:
                    continue

                sender = html.escape(e['from'])
                subject = html.escape(e['subject'])
                snippet = html.escape(e['snippet'])
                bg_color = "#fff7e600" if e['unread'] else "#f9f9f9"

                with st.container():
                    st.markdown(f"""
                        <div style='padding:10px; border:1px solid #ddd; border-radius:10px;
                        margin:6px 0; background:{bg_color}; box-shadow:1px 1px 4px rgba(0,0,0,0.05);'>
                            <b>From:</b> {sender}<br>
                            <b>Subject:</b> {subject}<br>
                            <small>{snippet}</small><br>
                            <i style='color:gray'>{'Unread' if e['unread'] else 'Read'}</i>
                        </div>
                    """, unsafe_allow_html=True)

                    if st.button(f"📖 Read: {subject}", key=e['id']):
                        with st.expander(f"📩 Email: {subject}", expanded=True):
                            content = read_email(service, e['id'])
                            st.write(content)
                    st.divider()

# =====================================================
# 🔍 SEARCH EMAIL TAB
# =====================================================
with tabs[1]:
    st.subheader("🔍 Search Emails")
    query = st.text_input("Enter Gmail search query (e.g., from:boss, subject:report, has:attachment)")
    if st.button("Search Emails"):
        results = search_emails(service, query)
        if not results:
            st.warning("No matching emails found.")
        else:
            st.success(f"Found {len(results)} result(s).")
            for mail in results:
                sender = html.escape(mail['from'])
                subject = html.escape(mail['subject'])
                st.markdown(f"**📤 From:** {sender}<br>**📌 Subject:** {subject}", unsafe_allow_html=True)
                if st.button(f"📖 Read: {subject}", key=mail['id']):
                    content = read_email(service, mail['id'])
                    st.text_area("Email Content:", content, height=250)
                st.divider()

# =====================================================
# ✉️ SEND EMAIL TAB
# =====================================================
with tabs[2]:
    st.subheader("✉️ Compose and Send Email")

    to = st.text_input("Recipient Email")
    subject = st.text_input("Subject")
    body = st.text_area("Message Body", height=200)

    if st.button("📨 Send Email"):
        if to and subject and body:
            try:
                send_email(service, to, subject, body)
                st.success("✅ Email sent successfully!")
            except Exception as e:
                st.error(f"❌ Failed to send email: {e}")
        else:
            st.warning("Please fill all fields before sending.")

# =====================================================
# 🛒 AMAZON PRODUCT SEARCH TAB
# =====================================================
with tabs[3]:
    st.subheader("🛒 Amazon Product Search")

    keyword_amazon = st.text_input("Enter product keyword for Amazon (e.g., iPhone, laptop, shoes)")
    if st.button("🔍 Search Amazon Products"):
        if not keyword_amazon:
            st.warning("Please enter a product name to search.")
        else:
            with st.spinner("Fetching Amazon products..."):
                products = search_amazon_products(keyword_amazon)

            if not products:
                st.warning("No Amazon products found.")
            else:
                st.success(f"Found {len(products)} products on Amazon. Showing top 10:")
                for p in products[:10]:
                    title = p.get("product_title") or p.get("title")
                    price = p.get("product_price") or p.get("price")
                    link = p.get("product_url") or p.get("url")
                    image = p.get("product_photo") or p.get("main_image")

                    with st.container():
                        cols = st.columns([1, 3])
                        with cols[0]:
                            if image:
                                st.image(image, width=120)
                        with cols[1]:
                            st.markdown(f"### {title}")
                            if price:
                                st.write(f"💰 **Price:** {price}")
                            if link:
                                st.markdown(f"[View Product 🔗]({link})")
                        st.divider()

# =====================================================
# 🏬 WALMART PRODUCT SEARCH TAB
# =====================================================
with tabs[4]:
    st.subheader("🏬 Walmart Product Search")

    keyword_walmart = st.text_input("Enter product keyword for Walmart (e.g., shoes, TV, headphones)")
    if st.button("🔍 Search Walmart Products"):
        if not keyword_walmart:
            st.warning("Please enter a product name to search.")
        else:
            with st.spinner("Fetching Walmart products..."):
                products = search_walmart_products(keyword_walmart)

            if not products:
                st.warning("No Walmart products found.")
            else:
                st.success(f"Found {len(products)} products on Walmart. Showing top 10:")
                for p in products[:10]:
                    title = p.get("name")
                    price = p.get("salePrice") or p.get("price")
                    link = p.get("product_url")
                    image = p.get("image")

                    with st.container():
                        cols = st.columns([1, 3])
                        with cols[0]:
                            if image:
                                st.image(image, width=120)
                        with cols[1]:
                            st.markdown(f"### {title}")
                            if price:
                                st.write(f"💰 **Price:** {price}")
                            if link:
                                st.markdown(f"[View Product 🔗]({link})")
                        st.divider()
