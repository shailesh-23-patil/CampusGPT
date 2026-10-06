/* =========================================================
   CAMPUSGPT — JAVASCRIPT
   Flask + HTML + CSS + Gemini RAG
========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    const heroScene = document.getElementById("heroScene");

    if (heroScene) {
        const heroSection = heroScene.closest(".hero-section");
        const leftCodeTrack = document.getElementById("codeTrackLeft");
        const rightCodeTrack = document.getElementById("codeTrackRight");
        let scrollFrame = 0;

        [leftCodeTrack, rightCodeTrack].forEach(track => {
            if (!track) return;
            const code = track.textContent.trim();
            track.textContent = `${code}\n\n${code}\n\n${code}`;
        });

        const updateHeroScene = () => {
            if (!heroSection) return;

            const sectionBounds = heroSection.getBoundingClientRect();
            const scrollDistance = Math.max(
                1,
                heroSection.offsetHeight - heroScene.offsetHeight
            );
            const progress = Math.min(
                1,
                Math.max(0, -sectionBounds.top / scrollDistance)
            );
            const motionScale = window.matchMedia(
                "(prefers-reduced-motion: reduce)"
            ).matches ? 0.45 : 1;

            heroScene.style.setProperty(
                "--left-code-scroll",
                `${-progress * 920 * motionScale}px`
            );
            heroScene.style.setProperty(
                "--right-code-scroll",
                `${progress * 720 * motionScale}px`
            );
        };

        const requestSceneUpdate = () => {
            if (scrollFrame) return;
            scrollFrame = window.requestAnimationFrame(() => {
                scrollFrame = 0;
                updateHeroScene();
            });
        };

        window.addEventListener("scroll", requestSceneUpdate, { passive: true });
        window.addEventListener("resize", requestSceneUpdate);
        updateHeroScene();
    }

    /* =====================================================
       ELEMENTS
    ===================================================== */

    const pdfInput = document.getElementById("pdfInput");
    const uploadCard = document.getElementById("uploadCard");
    const fileList = document.getElementById("fileList");

    const documentCount =
        document.getElementById("documentCount");

    const chunkCount =
        document.getElementById("chunkCount");

    const processButton =
        document.getElementById("processButton");

    const chatContainer =
        document.getElementById("chatContainer");

    const questionInput =
        document.getElementById("questionInput");

    const sendButton =
        document.getElementById("sendButton");

    const suggestions =
        document.querySelectorAll(".suggestion");


    /* =====================================================
       GEMINI API KEY ELEMENTS
    ===================================================== */

    const apiKeyInput =
        document.getElementById("apiKeyInput");

    const connectButton =
        document.getElementById("connectButton");

    const apiStatus =
        document.getElementById("apiStatus");


    /* =====================================================
       SELECTED FILES
    ===================================================== */

    let selectedFiles = [];


    /* =====================================================
       GEMINI API CONNECTION
    ===================================================== */

    if (connectButton) {

        connectButton.addEventListener(
            "click",
            connectGemini
        );

    }


    async function connectGemini() {

        if (!apiKeyInput) return;

        const apiKey =
            apiKeyInput.value.trim();


        if (!apiKey) {

            setApiStatus(
                "🔴 Please enter your Gemini API key.",
                "#dc2626"
            );

            return;

        }


        connectButton.disabled = true;

        connectButton.textContent =
            "Connecting...";


        setApiStatus(
            "🟡 Connecting to Gemini...",
            "#d97706"
        );


        try {

            const response =
                await fetch("/set-api-key", {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        api_key: apiKey
                    })

                });


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.error ||
                    "Failed to connect Gemini."
                );

            }


            /*
             * The Flask route accepts the key
             * and creates the Gemini client.
             *
             * Now test the actual Gemini connection.
             */

            const testResponse =
                await fetch("/test-gemini");


            const testData =
                await testResponse.json();


            if (!testResponse.ok) {

                throw new Error(
                    testData.error ||
                    "Gemini API key could not be verified."
                );

            }


            setApiStatus(
                "🟢 Gemini connected successfully.",
                "#16a34a"
            );


            connectButton.textContent =
                "✓ Connected";


            /*
             * Do not keep displaying the key.
             */

            apiKeyInput.value = "";

            apiKeyInput.placeholder =
                "Gemini API connected";


        } catch (error) {

            console.error(
                "Gemini connection error:",
                error
            );


            setApiStatus(
                "🔴 " +
                (
                    error.message ||
                    "Connection failed."
                ),
                "#dc2626"
            );


            connectButton.textContent =
                "Connect Gemini";

        }


        connectButton.disabled = false;

    }


    function setApiStatus(message, color) {

        if (!apiStatus) return;

        apiStatus.textContent = message;

        apiStatus.style.color = color;

    }


    /* =====================================================
       FILE INPUT
    ===================================================== */

    if (pdfInput) {

        pdfInput.addEventListener(
            "change",
            (event) => {

                const files =
                    Array.from(
                        event.target.files
                    );

                addFiles(files);

                /*
                 * Reset input so the same file
                 * can be selected again.
                 */

                pdfInput.value = "";

            }
        );

    }


    /* =====================================================
       ADD FILES
    ===================================================== */

    function addFiles(files) {

        const pdfFiles =
            files.filter(
                file =>
                    file.type === "application/pdf" ||
                    file.name.toLowerCase().endsWith(".pdf")
            );


        if (pdfFiles.length === 0) {

            showSystemMessage(
                "Please select PDF files only."
            );

            return;

        }


        pdfFiles.forEach(file => {

            const alreadyExists =
                selectedFiles.some(
                    existing =>
                        existing.name === file.name &&
                        existing.size === file.size
                );


            if (!alreadyExists) {

                selectedFiles.push(file);

            }

        });


        updateFileList();

    }


    /* =====================================================
       UPDATE FILE LIST
    ===================================================== */

    function updateFileList() {

        if (!fileList) return;


        fileList.innerHTML = "";


        if (documentCount) {
            documentCount.textContent = selectedFiles.length;

        }


        selectedFiles.forEach(
            (file, index) => {

                const fileItem =
                    document.createElement("div");


                fileItem.className =
                    "file-item";


                fileItem.innerHTML = `

                    <div class="file-icon">
                        📄
                    </div>

                    <div class="file-info">

                        <span class="file-name">
                            ${escapeHTML(file.name)}
                        </span>

                        <span class="file-size">
                            ${formatFileSize(file.size)}
                        </span>

                    </div>

                    <div
                        style="
                            display:flex;
                            align-items:center;
                            gap:10px;
                        "
                    >

                        <span
                            style="
                                color:#16a34a;
                                font-size:9px;
                                font-weight:700;
                            "
                        >
                            ✓ Ready
                        </span>

                        <button
                            class="remove-file"
                            data-index="${index}"
                            title="Remove file"
                            type="button"
                        >
                            ✕
                        </button>

                    </div>

                `;


                fileList.appendChild(fileItem);

            }
        );


        /*
         * Remove file buttons
         */

        document
            .querySelectorAll(".remove-file")
            .forEach(button => {

                button.addEventListener(
                    "click",
                    () => {

                        const index =
                            Number(
                                button.dataset.index
                            );


                        selectedFiles.splice(
                            index,
                            1
                        );


                        updateFileList();

                    }
                );

            });

    }


    /* =====================================================
       DRAG & DROP
    ===================================================== */

    if (uploadCard) {

        uploadCard.addEventListener(
            "dragover",
            event => {

                event.preventDefault();

                uploadCard.classList.add(
                    "drag-over"
                );

            }
        );


        uploadCard.addEventListener(
            "dragleave",
            () => {

                uploadCard.classList.remove(
                    "drag-over"
                );

            }
        );


        uploadCard.addEventListener(
            "drop",
            event => {

                event.preventDefault();

                uploadCard.classList.remove(
                    "drag-over"
                );


                const files =
                    Array.from(
                        event.dataTransfer.files
                    );


                addFiles(files);

            }
        );

    }


    /* =====================================================
       PROCESS BUTTON
    ===================================================== */

    if (processButton) {

        processButton.addEventListener(
            "click",
            async () => {

                if (selectedFiles.length === 0) {

                    showSystemMessage(
                        "Please upload at least one PDF before processing."
                    );

                    return;

                }


                processButton.disabled = true;

                processButton.innerHTML =
                    "⏳ Processing study material...";


                try {

                    const formData =
                        new FormData();


                    selectedFiles.forEach(
                        file => {

                            formData.append(
                                "files",
                                file
                            );

                        }
                    );

                    const response =
                        await fetch(
                            "/process",
                            {
                                method: "POST",
                                body: formData
                            }
                        );


                    const data =
                        await response.json();


                    if (!response.ok) {

                        throw new Error(
                            data.error ||
                            "Processing failed."
                        );

                    }


                    /*
                     * Update dashboard
                     */

                    if (documentCount) {

                        documentCount.textContent =
                            data.documents ||
                            selectedFiles.length;

                    }


                    updateChunkCount(
                        data.chunks || 0
                    );


                    processButton.innerHTML =
                        "✓ Study Material Ready";


                    processButton.style.background =
                        "linear-gradient(135deg,#059669,#10b981)";


                    showSystemMessage(
                        `Successfully processed ${
                            data.documents ||
                            selectedFiles.length
                        } document(s).`
                    );


                } catch (error) {

                    console.error(error);


                    processButton.innerHTML =
                        "⚡ Process Study Material";


                    processButton.style.background =
                        "";


                    showSystemMessage(
                        error.message ||
                        "Something went wrong while processing the PDFs."
                    );

                }


                processButton.disabled = false;

            }
        );

    }


    /* =====================================================
       SEND BUTTON
    ===================================================== */

    if (sendButton) {

        sendButton.addEventListener(
            "click",
            sendQuestion
        );

    }


    /* =====================================================
       ENTER KEY
    ===================================================== */

    if (questionInput) {

        questionInput.addEventListener(
            "keydown",
            event => {

                if (
                    event.key === "Enter" &&
                    !event.shiftKey
                ) {

                    event.preventDefault();

                    sendQuestion();

                }

            }
        );

    }


    /* =====================================================
       SEND QUESTION
    ===================================================== */

    async function sendQuestion() {

        if (!questionInput) return;


        const question =
            questionInput.value.trim();


        if (!question) return;


        /*
         * Add user message
         */

        addMessage(
            "user",
            question
        );


        questionInput.value = "";


        /*
         * Loading message
         */

        const loadingMessage =
            addLoadingMessage();


        if (sendButton) {

            sendButton.disabled = true;

        }


        try {

            const response =
                await fetch(
                    "/ask",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({
                            question: question
                        })

                    }
                );


            const data =
                await response.json();


            removeLoadingMessage(
                loadingMessage
            );


            if (!response.ok) {

                throw new Error(
                    data.error ||
                    "Unable to get an answer."
                );

            }


            addMessage(
                "ai",
                data.answer,
                data.sources || []
            );


        } catch (error) {

            console.error(
                "Question error:",
                error
            );


            removeLoadingMessage(
                loadingMessage
            );


            addMessage(
                "ai",
                "⚠️ " +
                (
                    error.message ||
                    "Something went wrong."
                )
            );

        }


        if (sendButton) {

            sendButton.disabled = false;

        }


        questionInput.focus();

    }


    /* =====================================================
       SUGGESTED QUESTIONS
    ===================================================== */

    suggestions.forEach(
        suggestion => {

            suggestion.addEventListener(
                "click",
                () => {

                    const question =
                        suggestion.dataset.question;


                    if (!questionInput) return;


                    questionInput.value =
                        question;


                    sendQuestion();

                }
            );

        }
    );


    /* =====================================================
       ADD CHAT MESSAGE
    ===================================================== */

    function addMessage(
        type,
        text,
        sources = []
    ) {

        if (!chatContainer) return;


        /*
         * Remove welcome message
         */

        const welcome =
            chatContainer.querySelector(
                ".welcome-message"
            );


        if (welcome) {

            welcome.remove();

        }


        const message =
            document.createElement("div");


        message.className =
            `message ${type}`;


        const avatar =
            type === "user"
                ? "👤"
                : "🎓";


        const name =
            type === "user"
                ? "You"
                : "CampusGPT";


        message.innerHTML = `

            <div class="message-avatar">
                ${avatar}
            </div>

            <div class="message-body">

                <div class="message-content">

                    ${formatMessage(text)}

                </div>

            </div>

        `;


        chatContainer.appendChild(
            message
        );


        /*
         * Add sources for AI answer
         */

        if (
            type === "ai" &&
            sources &&
            sources.length > 0
        ) {

            addSources(
                message,
                sources
            );

        }


        scrollToBottom();

    }


    /* =====================================================
       ADD SOURCES
    ===================================================== */

    function addSources(
        messageElement,
        sources
    ) {

        const body =
            messageElement.querySelector(
                ".message-body"
            );


        if (!body) return;


        const sourceBox =
            document.createElement("div");


        sourceBox.className =
            "message-sources";


        sources.forEach(source => {

            const sourceTag =
                document.createElement("div");


            sourceTag.className =
                "source-tag";


            const sourceName =
                source.source ||
                "Document";


            const page =
                source.page ||
                "-";


            let text =
                `📄 ${sourceName} • Page ${page}`;


            if (
                source.score !== undefined
            ) {

                text +=
                    ` • Similarity ${
                        Number(
                            source.score
                        ).toFixed(4)
                    }`;

            }


            sourceTag.textContent =
                text;


            sourceBox.appendChild(
                sourceTag
            );

        });


        body.appendChild(
            sourceBox
        );

    }


    /* =====================================================
       LOADING MESSAGE
    ===================================================== */

    function addLoadingMessage() {

        if (!chatContainer) return null;


        const message =
            document.createElement("div");


        message.className =
            "message ai";


        message.innerHTML = `

            <div class="message-avatar">
                🎓
            </div>

            <div class="message-body">

                <div class="message-content">

                    <div class="loading-message">

                        <span>
                            🔎 Searching your study material...
                        </span>

                        <span class="loading-dots">

                            <span></span>
                            <span></span>
                            <span></span>

                        </span>

                    </div>

                </div>

            </div>

        `;


        chatContainer.appendChild(
            message
        );


        scrollToBottom();


        return message;

    }


    /* =====================================================
       REMOVE LOADING MESSAGE
    ===================================================== */

    function removeLoadingMessage(
        element
    ) {

        if (element) {

            element.remove();

        }

    }


    /* =====================================================
       SYSTEM MESSAGE
    ===================================================== */

    function showSystemMessage(
        message
    ) {

        if (!chatContainer) return;


        const element =
            document.createElement("div");


        element.style.cssText = `

            background:#fff7ed;

            border:1px solid #fed7aa;

            color:#9a3412;

            padding:11px 14px;

            border-radius:11px;

            margin-bottom:12px;

            font-size:11px;

            font-weight:650;

        `;


        element.textContent =
            message;


        chatContainer.appendChild(
            element
        );


        scrollToBottom();


        setTimeout(
            () => {

                if (element) {

                    element.remove();

                }

            },
            5000
        );

    }


    /* =====================================================
       UPDATE CHUNK COUNT
    ===================================================== */

    function updateChunkCount(
        count
    ) {

        const element =
            document.getElementById(
                "chunkCount"
            );


        if (element) {

            element.textContent =
                count;

        }

    }


    /* =====================================================
       FILE SIZE
    ===================================================== */

    function formatFileSize(
        bytes
    ) {

        if (bytes === 0) {

            return "0 Bytes";

        }


        const units = [
            "Bytes",
            "KB",
            "MB",
            "GB"
        ];


        const i =
            Math.floor(
                Math.log(bytes) /
                Math.log(1024)
            );


        return (
            parseFloat(
                (
                    bytes /
                    Math.pow(
                        1024,
                        i
                    )
                ).toFixed(2)
            ) +
            " " +
            units[i]
        );

    }


    /* =====================================================
       ESCAPE HTML
    ===================================================== */

    function escapeHTML(
        value
    ) {

        const div =
            document.createElement(
                "div"
            );


        div.textContent =
            value;


        return div.innerHTML;

    }


    /* =====================================================
       FORMAT AI MESSAGE
    ===================================================== */

    function formatMessage(
        text
    ) {

        if (!text) {

            return "";

        }


        let safe =
            escapeHTML(text);


        /*
         * Bold:
         * **text**
         */

        safe =
            safe.replace(
                /\*\*(.*?)\*\*/g,
                "<strong>$1</strong>"
            );


        /*
         * Numbered list formatting
         */

        safe =
            safe.replace(
                /^(\d+)\.\s/gm,
                "<strong>$1.</strong> "
            );


        /*
         * Bullet formatting
         */

        safe =
            safe.replace(
                /^[-•]\s/gm,
                "• "
            );


        /*
         * New lines
         */

        safe =
            safe.replace(
                /\n/g,
                "<br>"
            );


        return safe;

    }


    /* =====================================================
       SCROLL CHAT
    ===================================================== */

    function scrollToBottom() {

        if (!chatContainer) return;


        setTimeout(
            () => {

                chatContainer.scrollTo({

                    top:
                        chatContainer.scrollHeight,

                    behavior:
                        "smooth"

                });

            },
            50
        );

    }


    /* =====================================================
       INITIAL STATE
    ===================================================== */

    updateFileList();


});