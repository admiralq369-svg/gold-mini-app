let tg = window.Telegram.WebApp;
tg.expand();

let selectedPlanName = "";
let selectedPrice = 0;

function selectPlan(planName, price, days, element) {
    selectedPlanName = planName;
    selectedPrice = price;

    let cards = document.querySelectorAll('.plan-card');
    cards.forEach(card => card.classList.remove('active'));

    element.classList.add('active');

    document.getElementById('payment-details').style.display = 'block';
    
    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
}

function copyWallet() {
    let walletAddr = document.getElementById('wallet-addr').innerText;
    navigator.clipboard.writeText(walletAddr).then(() => {
        alert("تم نسخ عنوان المحفظة بنجاح!");
    }).catch(err => {
        alert("تعذر النسخ تلقائياً، يرجى نسخه يدوياً.");
    });
}

function confirmPayment() {
    if (!selectedPlanName) {
        alert("يرجى اختيار خطة أولاً");
        return;
    }

    let paymentData = {
        action: "payment_submitted",
        plan: selectedPlanName,
        price: selectedPrice,
        user_id: tg.initDataUnsafe?.user?.id || "غير معروف",
        username: tg.initDataUnsafe?.user?.username || "بدون يوزر"
    };

    tg.sendData(JSON.stringify(paymentData));
    tg.close();
}
