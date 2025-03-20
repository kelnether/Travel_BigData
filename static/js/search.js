async function searchSpot() {
    const user_id = "UserA";  // 假设用户ID
    const poiName = document.getElementById("poiName").value.trim();

    if (!poiName) {
        document.getElementById("result").innerText = "❌ 请输入景点名称！";
        return;
    }

    const response = await fetch("/search_api", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id, poiName })
    });

    const data = await response.json();

    const resultContainer = document.getElementById("result");
    const spotsContainer = document.getElementById("spots-container");

    if (data.found) {
        // 显示成功消息
        resultContainer.innerText = data.message;

        // 清空旧的推荐结果
        spotsContainer.innerHTML = "";

        // 创建景点列表
        data.spots.forEach(spot => {
            const spotDiv = document.createElement("div");
            spotDiv.classList.add("spot-item");

            spotDiv.innerHTML = `
                <img src="${spot.image}" alt="${spot.name}" style="width: 100px; height: 100px;">
                <h3>${spot.name}</h3>
                <p>类别: ${spot.category}</p>
                <p>评分: ${spot.score}</p>
            `;

            spotsContainer.appendChild(spotDiv);
        });

    } else {
        // 搜索失败
        resultContainer.innerText = data.message;
        spotsContainer.innerHTML = ""; // 清空之前的内容
    }
}
