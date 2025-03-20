// 📌 确保 JSON 解析时使用 UTF-8
document.addEventListener("DOMContentLoaded", function () {
    console.log("📊 旅游大数据页面加载完成");
    document.documentElement.lang = "zh"; // 确保 HTML 语言正确
});

// 📌 触发景点搜索
async function searchSpot() {
    const poiName = document.getElementById("poiName").value.trim();
    const user_id = "UserA"; // 假设的登录用户

    if (!poiName) {
        alert("❌ 请输入景点名称！");
        return;
    }

    const response = await fetch("/search_api", {
        method: "POST",
        headers: { "Content-Type": "application/json; charset=UTF-8" }, // 确保 UTF-8 编码
        body: JSON.stringify({ user_id, poiName })
    });

    const data = await response.json();
    updateSearchResult(data.spots);
}

// 📌 渲染搜索结果
function updateSearchResult(spots) {
    const searchDiv = document.getElementById("search-result");
    const outputDiv = document.getElementById("search-output");

    if (spots.length > 0) {
        outputDiv.innerHTML = spots.map(spot => `
            <div class="spot-card">
                <img src="${spot.image}" alt="${spot.name}">
                <div class="spot-info">
                    <div class="spot-name">${spot.name}</div>
                    <div class="spot-category">${spot.category}</div>
                    <div class="spot-score">评分: ⭐${spot.score}</div>
                </div>
            </div>
        `).join("");
    } else {
        outputDiv.innerHTML = "<p>❌ 未找到相关景点</p>";
    }
    searchDiv.style.display = "block";
}

// 📌 获取推荐景点
async function fetchRecommendations() {
    const user_id = "UserA"; // 假设的用户 ID

    const response = await fetch("/get_recommendations", {
        method: "POST",
        headers: { "Content-Type": "application/json; charset=UTF-8" },
        body: JSON.stringify({ user_id })
    });

    const data = await response.json();
    updateRecommendations(data.recommendations);
}

// 📌 渲染推荐景点
function updateRecommendations(recommendations) {
    const recommendationsDiv = document.getElementById("recommendations");
    recommendationsDiv.innerHTML = "<h2>🌟 你的个性化推荐</h2>";

    recommendations.forEach(spot => {
        recommendationsDiv.innerHTML += `
            <div class="spot-card">
                <img src="${spot.image}" alt="${spot.name}">
                <div class="spot-info">
                    <div class="spot-name">${spot.name}</div>
                    <div class="spot-score">评分: ⭐${spot.score}</div>
                </div>
            </div>
        `;
    });
}

// 📌 在页面加载时调用推荐函数
window.onload = fetchRecommendations;
