import re

with open('library/templates/base.html', 'r') as f:
    content = f.read()

# Remove the broken part at the end
# The broken part starts with "<!-- Floating AI Chat Widget -->" and goes to "</html>"
broken_part_pattern = re.compile(r'<!-- Floating AI Chat Widget -->.*</html>', re.DOTALL)
content = broken_part_pattern.sub('', content)

# Redefine the entire chat widget as a clean block
chat_widget = """<!-- Floating AI Chat Widget -->
    <div id="aiChatWindowContainer" class="fixed bottom-6 right-6 z-[9999]">
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
                        <h3 class="font-bold text-sm">AI Assistant</h3>
                        <p class="text-[10px] text-orange-100 font-medium uppercase tracking-wider">Online</p>
                    </div>
                </div>
                <button id="closeChatBtn" class="w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 transition-all flex items-center justify-center text-white">
                    <i class="fas fa-times text-sm"></i>
                </button>
            </div>

            <!-- Messages Area -->
            <div id="chatMessages" class="flex-1 overflow-y-auto p-5 space-y-4 bg-gray-50/50 scroll-smooth pb-8 relative">
                <div class="flex justify-start items-start space-x-3">
                    <div class="w-8 h-8 rounded-full bg-gradient-to-br from-orange-100 to-orange-50 flex items-center justify-center flex-shrink-0 text-orange-600 shadow-sm border border-orange-100">
                        <i class="fas fa-robot text-xs"></i>
                    </div>
                    <div class="bg-white text-gray-700 rounded-2xl rounded-tl-none px-4 py-3 max-w-[85%] text-xs leading-relaxed border border-gray-100 shadow-sm">
                        Hi! I'm your Book Hub assistant. How can I help you today?
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

            <!-- Action Bar -->
            <div id="cameraContainer" class="hidden relative w-full h-48 bg-black">
                <video id="video" class="w-full h-full object-cover" autoplay playsinline></video>
                <button id="captureBtn" class="absolute bottom-2 left-1/2 -translate-x-1/2 w-10 h-10 bg-white rounded-full border-4 border-orange-600 shadow-lg"></button>
                <button id="stopCameraBtn" class="absolute top-2 right-2 text-white bg-black/50 w-6 h-6 rounded-full flex items-center justify-center"><i class="fas fa-times text-xs"></i></button>
            </div>

            <!-- Input Area -->
            <div class="p-4 bg-white border-t border-gray-100 z-10">
                <div class="flex items-center space-x-2 mb-3 overflow-x-auto pb-1" style="scrollbar-width: none;">
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
                    <input type="text" id="aiSearchInput" placeholder="Message Book Hub..." class="w-full bg-gray-50 border border-gray-200 rounded-full pl-4 pr-12 py-2.5 text-sm text-gray-700 focus:outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-200 transition-all shadow-inner" autocomplete="off">
                    <button type="submit" class="absolute right-1.5 w-8 h-8 bg-orange-600 text-white rounded-full hover:bg-orange-700 transition flex items-center justify-center shadow-md">
                        <i class="fas fa-paper-plane text-xs -ml-0.5"></i>
                    </button>
                </form>
            </div>
        </div>
    </div>
</body>
</html>"""

# Append the widget and closing tags
content = content.strip() + '\n' + chat_widget

with open('library/templates/base.html', 'w') as f:
    f.write(content)
