import re

with open('library/templates/base.html', 'r') as f:
    html = f.read()

# 1. Remove chatbotTrigger from nav
nav_trigger = re.compile(r'<!-- AI Chatbot Trigger in Nav -->.*?<button id="chatbotTrigger".*?</button>', re.DOTALL)
html = nav_trigger.sub('', html)

# 2. Replace aiChatPopover entirely
popover_replacement = """    <!-- Floating AI Chat Widget -->
    <div class="fixed bottom-6 right-6 z-[9999] flex flex-col items-end">
        
        <!-- Modern Chat Window -->
        <div id="aiChatPopover" class="mb-4 bg-white rounded-2xl shadow-2xl border border-gray-100 overflow-hidden flex flex-col transition-all duration-300 transform origin-bottom-right w-[350px] h-[500px] opacity-0 scale-95 translate-y-4 pointer-events-none" style="display: none;">
            
            <!-- Header -->
            <div class="bg-gradient-to-r from-orange-600 to-orange-500 px-5 py-4 flex justify-between items-center text-white">
                <div class="flex items-center space-x-3">
                    <div class="relative">
                        <div class="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center backdrop-blur-sm">
                            <i class="fas fa-robot text-white text-lg"></i>
                        </div>
                        <div class="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-400 border-2 border-orange-500 rounded-full"></div>
                    </div>
                    <div>
                        <h3 class="font-bold text-sm">{% trans "AI Assistant" %}</h3>
                        <p class="text-[10px] text-orange-100 font-medium uppercase tracking-wider">{% trans "Online" %}</p>
                    </div>
                </div>
                <button id="closeChatBtn" class="w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 transition-all flex items-center justify-center text-white">
                    <i class="fas fa-times text-sm"></i>
                </button>
            </div>

            <!-- Messages Area -->
            <div id="chatMessages" class="flex-1 overflow-y-auto p-5 space-y-4 bg-gray-50/50 scroll-smooth pb-8 relative">
                <!-- Welcome Message -->
                <div class="flex justify-start items-start space-x-3">
                    <div class="w-8 h-8 rounded-full bg-gradient-to-br from-orange-100 to-orange-50 flex items-center justify-center flex-shrink-0 text-orange-600 shadow-sm border border-orange-100">
                        <i class="fas fa-robot text-xs"></i>
                    </div>
                    <div class="bg-white text-gray-700 rounded-2xl rounded-tl-none px-4 py-3 max-w-[85%] text-xs leading-relaxed border border-gray-100 shadow-sm">
                        {% trans "Hi! I'm your Book Hub assistant. How can I help you today?" %}
                    </div>
                </div>
            </div>

            <!-- Typing Indicator -->
            <div id="typingIndicator" class="hidden px-5 pb-3 flex justify-start items-center space-x-3 absolute bottom-[72px] left-0 bg-gradient-to-t from-white to-transparent w-full pt-4 pointer-events-none">
                <div class="w-8 h-8 rounded-full bg-gradient-to-br from-orange-100 to-orange-50 flex items-center justify-center flex-shrink-0 text-orange-600 shadow-sm border border-orange-100 pointer-events-auto">
                    <i class="fas fa-robot text-xs"></i>
                </div>
                <div class="flex space-x-1.5 bg-white px-4 py-2.5 rounded-2xl rounded-tl-none border border-gray-100 shadow-sm pointer-events-auto">
                    <div class="w-1.5 h-1.5 bg-orange-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                    <div class="w-1.5 h-1.5 bg-orange-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                    <div class="w-1.5 h-1.5 bg-orange-400 rounded-full animate-bounce"></div>
                </div>
            </div>

            <!-- Action Bar (Hidden Camera View) -->
            <div id="cameraContainer" class="hidden relative w-full h-48 bg-black">
                <video id="video" class="w-full h-full object-cover" autoplay playsinline></video>
                <button id="captureBtn" class="absolute bottom-2 left-1/2 -translate-x-1/2 w-10 h-10 bg-white rounded-full border-4 border-orange-600 shadow-lg"></button>
                <button id="stopCameraBtn" class="absolute top-2 right-2 text-white bg-black/50 w-6 h-6 rounded-full flex items-center justify-center"><i class="fas fa-times text-xs"></i></button>
            </div>

            <!-- Input Area -->
            <div class="p-4 bg-white border-t border-gray-100 z-10">
                <div class="flex items-center space-x-2 mb-3 overflow-x-auto pb-1 relative z-10" style="scrollbar-width: none;">
                    <button id="voiceBtn" class="flex-shrink-0 w-8 h-8 rounded-full bg-gray-50 text-gray-500 hover:bg-orange-50 hover:text-orange-600 transition shadow-sm border border-gray-100 flex items-center justify-center" title="Voice Input">
                        <i class="fas fa-microphone text-xs"></i>
                    </button>
                    <button id="cameraBtn" class="flex-shrink-0 w-8 h-8 rounded-full bg-gray-50 text-gray-500 hover:bg-blue-50 hover:text-blue-600 transition shadow-sm border border-gray-100 flex items-center justify-center" title="Open Camera">
                        <i class="fas fa-camera text-xs"></i>
                    </button>
                    <label for="fileInput" class="flex-shrink-0 w-8 h-8 rounded-full bg-gray-50 text-gray-500 hover:bg-purple-50 hover:text-purple-600 transition shadow-sm border border-gray-100 flex items-center justify-center cursor-pointer" title="Upload File">
                        <i class="fas fa-paperclip text-xs"></i>
                    </label>
                    <input type="file" id="fileInput" class="hidden" accept="image/*,.pdf,.doc,.docx">
                </div>
                
                <form id="aiChatForm" class="relative flex items-center">
                    <input type="text" id="aiSearchInput" placeholder="{% trans 'Message Book Hub...' %}"
                        class="w-full bg-gray-50 border border-gray-200 rounded-full pl-4 pr-12 py-2.5 text-sm text-gray-700 focus:outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-200 transition-all shadow-inner" autocomplete="off">
                    <button type="submit" class="absolute right-1.5 w-8 h-8 bg-orange-600 text-white rounded-full hover:bg-orange-700 transition flex items-center justify-center shadow-md">
                        <i class="fas fa-paper-plane text-xs -ml-0.5"></i>
                    </button>
                </form>
            </div>
        </div>

        <!-- Floating Toggle Button -->
        <button id="chatbotToggleBtn" class="w-14 h-14 sm:w-16 sm:h-16 rounded-full bg-gradient-to-r from-orange-600 to-orange-500 text-white flex items-center justify-center hover:shadow-lg transition-all duration-300 shadow-2xl hover:scale-110 active:scale-95 relative group border-2 border-white">
            <span class="absolute top-0 right-0 w-3.5 h-3.5 sm:w-4 sm:h-4 bg-red-500 border-2 border-white rounded-full flex items-center justify-center z-10" id="chatNotificationDot">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
            </span>
            
            <i class="fas fa-comment-dots text-xl sm:text-2xl transition-transform duration-300 transform absolute" id="toggleIconChat"></i>
            <i class="fas fa-times text-xl sm:text-2xl transition-transform duration-300 transform scale-0 absolute" id="toggleIconClose"></i>
        </button>
    </div>"""

popover_regex = re.compile(r'<!-- Modern Square Chat Window -->.*?</form>\s*</div>\s*</div>', re.DOTALL)
html = popover_regex.sub(popover_replacement, html)

# 3. JS Updates
js_old = """        const chatbotTrigger = document.getElementById('chatbotTrigger');
        const typingIndicator = document.getElementById('typingIndicator');"""
js_new = """        const chatbotToggleBtn = document.getElementById('chatbotToggleBtn');
        const chatNotificationDot = document.getElementById('chatNotificationDot');
        const toggleIconChat = document.getElementById('toggleIconChat');
        const toggleIconClose = document.getElementById('toggleIconClose');
        const typingIndicator = document.getElementById('typingIndicator');"""
html = html.replace(js_old, js_new)

js_open_old = """        function openChat() {
            if (isChatOpen) return;
            isChatOpen = true;
            chatPopover.style.display = 'flex';
            setTimeout(() => {
                chatPopover.classList.remove('opacity-0', 'scale-90', 'pointer-events-none');
                chatPopover.classList.add('opacity-100', 'scale-100');
            }, 10);
        }

        function closeChat() {
            if (!isChatOpen) return;
            isChatOpen = false;
            stopCamera();
            chatPopover.classList.remove('opacity-100', 'scale-100');
            chatPopover.classList.add('opacity-0', 'scale-90', 'pointer-events-none');
            setTimeout(() => {
                chatPopover.style.display = 'none';
            }, 300);
        }"""
        
# If scale-90 or scale-95 was there since I updated it to scale-90 in prev block
js_open_regex = re.compile(r'function openChat\(\) \{.*?(?=if \(chatbotTrigger\) \{)', re.DOTALL)

js_open_new = """function openChat() {
            if (isChatOpen) return;
            isChatOpen = true;
            if (chatNotificationDot) {
                chatNotificationDot.style.display = 'none';
            }
            chatPopover.style.display = 'flex';
            
            if (toggleIconChat && toggleIconClose) {
                toggleIconChat.style.transform = 'scale(0)';
                toggleIconClose.style.transform = 'scale(1) rotate(90deg)';
            }
            
            setTimeout(() => {
                chatPopover.classList.remove('opacity-0', 'scale-95', 'translate-y-4', 'pointer-events-none', 'scale-90');
                chatPopover.classList.add('opacity-100', 'scale-100', 'translate-y-0');
            }, 10);
            setTimeout(scrollToBottom, 100);
        }

        function closeChat() {
            if (!isChatOpen) return;
            isChatOpen = false;
            stopCamera();
            
            if (toggleIconChat && toggleIconClose) {
                toggleIconChat.style.transform = 'scale(1)';
                toggleIconClose.style.transform = 'scale(0) rotate(0deg)';
            }
            
            chatPopover.classList.remove('opacity-100', 'scale-100', 'translate-y-0');
            chatPopover.classList.add('opacity-0', 'scale-95', 'translate-y-4', 'pointer-events-none');
            setTimeout(() => {
                chatPopover.style.display = 'none';
            }, 300);
        }

        """

html = js_open_regex.sub(js_open_new, html)

js_trigger_old = """        if (chatbotTrigger) {
            chatbotTrigger.addEventListener('click', (e) => {
                e.stopPropagation();
                if (isChatOpen) closeChat();
                else openChat();
            });
        }"""
js_trigger_new = """        if (chatbotToggleBtn) {
            chatbotToggleBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                if (isChatOpen) closeChat();
                else openChat();
            });
        }"""
html = html.replace(js_trigger_old, js_trigger_new)

js_click_outside_old = """        document.addEventListener('click', (e) => {
            if (isChatOpen && !chatPopover.contains(e.target) && !chatbotTrigger.contains(e.target)) {
                closeChat();
            }
        });"""
js_click_outside_new = """        document.addEventListener('click', (e) => {
            if (isChatOpen && !chatPopover.contains(e.target) && !chatbotToggleBtn.contains(e.target)) {
                closeChat();
            }
        });"""
html = html.replace(js_click_outside_old, js_click_outside_new)

# Add typing dot animation to receive response
js_msg_old = """        function addMessageToChat(role, text, attachmentUrl = null) {"""
js_msg_new = """        // Simulate typing before adding AI response
        function addMessageToChat(role, text, attachmentUrl = null) {
            if (role === 'ai') {
                typingIndicator.classList.remove('hidden');
                scrollToBottom();
                setTimeout(() => {
                    typingIndicator.classList.add('hidden');
                    renderMessage(role, text, attachmentUrl);
                    
                    // Show notification dot if chat closed when received
                    if (!isChatOpen && chatNotificationDot) {
                        chatNotificationDot.style.display = 'flex';
                    }
                }, 800 + Math.random() * 1000); // 0.8s - 1.8s random typing delay
            } else {
                renderMessage(role, text, attachmentUrl);
            }
        }

        function renderMessage(role, text, attachmentUrl = null) {"""
html = html.replace(js_msg_old, js_msg_new)

# One small fix: if the chat receives message and uses typing indicator
js_receive_old = """                    if (response.ok) {
                        addMessageToChat('ai', data.response);
                    } else {
                        addMessageToChat('ai', '{% trans "Sorry, I encountered an error answering your request." %}');
                    }
                } catch (error) {
                    typingIndicator.classList.add('hidden');
                    addMessageToChat('ai', '{% trans "Connection error. Please try again." %}');
                }"""
js_receive_new = """                    if (response.ok) {
                        addMessageToChat('ai', data.response);
                    } else {
                        addMessageToChat('ai', '{% trans "Sorry, I encountered an error answering your request." %}');
                    }
                } catch (error) {
                    addMessageToChat('ai', '{% trans "Connection error. Please try again." %}');
                }"""

# Fix the 'typingIndicator.classList.add('hidden');' in submit handler because addMessageToChat handles it
js_submit_old = """                const message = searchInput.value.trim();
                if (!message) return;

                addMessageToChat('user', message);
                searchInput.value = '';
                typingIndicator.classList.remove('hidden');
                scrollToBottom();"""
js_submit_new = """                const message = searchInput.value.trim();
                if (!message) return;

                addMessageToChat('user', message);
                searchInput.value = '';
                scrollToBottom();"""
html = html.replace(js_submit_old, js_submit_new)

with open('library/templates/base.html', 'w') as f:
    f.write(html)
