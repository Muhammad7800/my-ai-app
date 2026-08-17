/* Pastdagi input va [+] tugmasi turgan qismni pastdan sal ko'tarish */
    div[data-testid="stVerticalBlock"] > div:has(div[data-testid="stChatInput"]) {
        position: fixed;
        bottom: 15px; /* Pastdan 15 piksel masofa */
        left: 50%;
        transform: translateX(-50%);
        width: 100%;
        max-width: 750px;
        background-color: #0e1117;
        padding: 10px 16px;
        z-index: 100;
        box-sizing: border-box;
        border-radius: 20px; /* Burchaklarini yumaloqlash */
    }
