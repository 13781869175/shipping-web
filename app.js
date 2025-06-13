document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('dropZone');
    const imageInput = document.getElementById('imageInput');
    const imagePreview = document.getElementById('imagePreview');
    const predictBtn = document.getElementById('predictBtn');
    const resultsDiv = document.getElementById('results');

    // 点击上传区域触发文件选择
    dropZone.addEventListener('click', () => {
        imageInput.click();
    });

    // 处理拖拽上传
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.background = '#f0f7ff';
    });

    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropZone.style.background = 'none';
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.background = 'none';
        const file = e.dataTransfer.files[0];
        handleFile(file);
    });

    // 处理文件选择
    imageInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        handleFile(file);
    });

    // 处理文件预览和启用预测按钮
    function handleFile(file) {
        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                imagePreview.src = e.target.result;
                predictBtn.disabled = false;
            };
            reader.readAsDataURL(file);
        }
    }

    // 处理预测请求
    predictBtn.addEventListener('click', async () => {
        try {
            predictBtn.disabled = true;
            predictBtn.textContent = '识别中...';
            
            // 创建FormData对象
            const formData = new FormData();
            formData.append('image', imageInput.files[0]);

            // 发送预测请求
            const response = await fetch('/predict', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            
            // 显示预测结果
            displayResults(result);
        } catch (error) {
            console.error('预测失败:', error);
            resultsDiv.innerHTML = '<p class="error">预测失败，请重试</p>';
        } finally {
            predictBtn.disabled = false;
            predictBtn.textContent = '开始识别';
        }
    });

    // 显��预测结果
    function displayResults(results) {
        resultsDiv.innerHTML = `
            <h4>识别结果：</h4>
            <p>${results.class_name}</p>
            <p>置信度：${(results.confidence * 100).toFixed(2)}%</p>
        `;
    }
}); 