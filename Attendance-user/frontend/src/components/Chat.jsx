import { useState, useEffect, useRef } from "react";
import {
  FiSend,
  FiPlus,
  FiSearch,
  FiSmile,
  FiChevronLeft,
  FiTrash2,
} from "react-icons/fi";
import { LS } from "../Utils/Resuse";
import clsx from "clsx";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import Picker from "emoji-picker-react";

const ipadr = import.meta.env.VITE_API_BASE_URL;

const formatTime = (isoString, withDate = false) => {
  if (!isoString) return "";
  const date = new Date(isoString);
  return withDate
    ? date.toLocaleString([], { dateStyle: "short", timeStyle: "short" })
    : date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
};

export default function Chat() {
  const [messages, setMessages] = useState({});
  const [newMessage, setNewMessage] = useState("");
  const [activeChat, setActiveChat] = useState({ id: "", name: "", chatId: "", type: "user" });
  const [contacts, setContacts] = useState([]);
  const [groups, setGroups] = useState([]);
  const [unread, setUnread] = useState({});
  const [searchTerm, setSearchTerm] = useState("");
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const [showGroupModal, setShowGroupModal] = useState(false);
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [groupName, setGroupName] = useState("");
  const [onlineUsers, setOnlineUsers] = useState([]);
  const [isConnected, setIsConnected] = useState(false);

  const userid = LS.get("userid");
  const position = LS.get("position");
  const ws = useRef(null);
  const chatEndRef = useRef(null);

  const buildChatId = (a, b) => [a, b].sort().join("_");

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, activeChat]);

  const getInitials = (name = "") => name.split(" ").map(n => n[0]).join("").toUpperCase();

  // --- Fetch contacts and groups ---
  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${ipadr}/get_all_users`);
        const data = await res.json();
        setContacts(data.filter(u => u.id !== userid));
      } catch (err) {
        console.error("Fetch users error:", err);
      }
    })();

    (async () => {
      try {
        const res = await fetch(`${ipadr}/get_user_groups/${userid}`);
        const data = await res.json();
        setGroups(data);
      } catch (err) {
        console.error("Fetch groups error:", err);
      }
    })();
  }, [userid]);

  // --- WebSocket connection ---
  const openWebSocket = (chatType = "user", chatId = "") => {
    ws.current?.close();
    const wsProtocol = ipadr.startsWith("https") ? "wss" : "ws";
    const host = ipadr.replace(/^https?:\/\//, "");
    const url =
      chatType === "group"
        ? `${wsProtocol}://${host}/ws/group/${chatId}`
        : `${wsProtocol}://${host}/ws/${userid}`;
    ws.current = new WebSocket(url);

    ws.current.onopen = () => setIsConnected(true);
    ws.current.onclose = () => setIsConnected(false);
    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (!data.chatId) return;
        setMessages(prev => ({
          ...prev,
          [data.chatId]: [...(prev[data.chatId] || []), data],
        }));
      } catch (err) {
        console.error("Invalid WS message:", err);
      }
    };
  };

  // --- Handle contact click ---
  const handleContactClick = async (contact) => {
    const chatId = buildChatId(userid, contact.id);
    setActiveChat({ id: contact.id, name: contact.name, chatId, type: "user" });
    setUnread(prev => ({ ...prev, [chatId]: 0 }));
    openWebSocket("user");
  };

  // --- Handle group click ---
  const handleGroupClick = (group) => {
    setActiveChat({ id: group._id, name: group.name, chatId: group._id, type: "group" });
    setUnread(prev => ({ ...prev, [group._id]: 0 }));
    openWebSocket("group", group._id);
  };

  // --- Send message ---
  const sendMessage = () => {
    if (!newMessage.trim() || !activeChat.chatId) return;
    const msg = {
      id: `temp-${Date.now()}`,
      from_user: userid,
      text: newMessage,
      timestamp: new Date().toISOString(),
      chatId: activeChat.chatId,
    };
    setMessages(prev => ({
      ...prev,
      [activeChat.chatId]: [...(prev[activeChat.chatId] || []), msg],
    }));
    ws.current?.send(JSON.stringify(msg));
    setNewMessage("");
  };

  const activeMessages = messages[activeChat.chatId] || [];
  const filteredContacts = contacts.filter(c =>
    c.name.toLowerCase().includes(searchTerm.toLowerCase())
  );
  const filteredGroups = groups.filter(g =>
    g.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="flex h-screen w-full bg-gradient-to-br from-white to-blue-50 text-gray-800 font-sans">
      {/* Sidebar */}
      <div className="w-72 bg-white border-r border-gray-200 flex flex-col shadow-sm">
        <div className="p-5 flex items-center justify-between border-b">
          <h1 className="text-xl font-semibold tracking-tight">Chat</h1>
          {position?.toLowerCase() === "manager" && (
            <button
              onClick={() => setShowGroupModal(true)}
              className="p-2 hover:bg-blue-100 rounded-full text-blue-600 transition"
            >
              <FiPlus />
            </button>
          )}
        </div>

        {/* Search Bar */}
        <div className="p-3">
          <div className="flex items-center gap-2 bg-gray-100 px-3 py-2 rounded-full focus-within:ring-2 ring-blue-400">
            <FiSearch className="text-gray-400" />
            <input
              type="text"
              placeholder="Search..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-transparent outline-none text-sm"
            />
          </div>
        </div>

        {/* Contacts & Groups */}
        <div className="flex-1 overflow-y-auto px-3 space-y-4 scrollbar-thin scrollbar-thumb-gray-200 scrollbar-track-gray-50">
          <div>
            <p className="text-xs font-medium text-gray-400 uppercase mb-2">Groups</p>
            {filteredGroups.map((g) => (
              <div
                key={g._id}
                className={clsx(
                  "p-3 rounded-xl flex items-center justify-between cursor-pointer hover:bg-blue-50 transition shadow-sm",
                  activeChat.chatId === g._id && "bg-blue-100"
                )}
                onClick={() => handleGroupClick(g)}
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-blue-200 flex items-center justify-center font-semibold text-blue-700">
                    {getInitials(g.name)}
                  </div>
                  <span className="font-medium">{g.name}</span>
                </div>
              </div>
            ))}
          </div>

          <div>
            <p className="text-xs font-medium text-gray-400 uppercase mb-2">Contacts</p>
            {filteredContacts.map((c) => (
              <div
                key={c.id}
                className={clsx(
                  "p-3 rounded-xl flex items-center justify-between cursor-pointer hover:bg-blue-50 transition shadow-sm",
                  activeChat.chatId === buildChatId(userid, c.id) && "bg-blue-100"
                )}
                onClick={() => handleContactClick(c)}
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center font-semibold text-gray-700">
                    {getInitials(c.name)}
                  </div>
                  <span className="font-medium">{c.name}</span>
                </div>
                {unread[buildChatId(userid, c.id)] > 0 && (
                  <span className="bg-red-500 text-white text-xs px-2 py-0.5 rounded-full">
                    {unread[buildChatId(userid, c.id)]}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Chat Window */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white p-4 border-b flex items-center gap-3 shadow-sm">
          <div className="w-12 h-12 rounded-xl bg-blue-200 flex items-center justify-center text-blue-700 font-semibold text-lg">
            {activeChat.id ? getInitials(activeChat.name) : "💬"}
          </div>
          <div>
            <h2 className="text-lg font-semibold">{activeChat.name || "Select a chat"}</h2>
            {activeChat.id && <p className="text-sm text-gray-400">{activeChat.id}</p>}
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gradient-to-b from-blue-50 to-white">
          {activeMessages.map((m) => {
            const isMine = m.from_user === userid;
            return (
              <div
                key={m.id}
                className={clsx("flex", isMine ? "justify-end" : "justify-start")}
              >
                <div
                  className={clsx(
                    "max-w-md px-4 py-3 rounded-2xl shadow-sm",
                    isMine
                      ? "bg-blue-100 text-gray-800 rounded-br-none"
                      : "bg-white border border-gray-200 rounded-bl-none"
                  )}
                >
                  <div className="text-sm">{m.text}</div>
                  <div className="text-xs text-gray-400 mt-1 text-right">
                    {formatTime(m.timestamp)}
                  </div>
                </div>
              </div>
            );
          })}
          <div ref={chatEndRef} />
        </div>

        {/* Input */}
        <div className="bg-white border-t p-3 flex items-center gap-3 shadow-inner relative">
          <button
            onClick={() => setShowEmojiPicker((prev) => !prev)}
            className="p-2 rounded-full hover:bg-gray-100 text-gray-500"
          >
            <FiSmile />
          </button>
          {showEmojiPicker && (
            <div className="absolute bottom-14 left-4 shadow-lg rounded-lg z-50">
              <Picker onEmojiClick={(e) => setNewMessage((prev) => prev + e.emoji)} />
            </div>
          )}
          <textarea
            rows={1}
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
              }
            }}
            placeholder="Type a message..."
            className="flex-1 border rounded-full px-4 py-2 text-sm focus:ring-2 focus:ring-blue-400 focus:outline-none"
          />
          <button
            onClick={sendMessage}
            disabled={!newMessage.trim()}
            className={clsx(
              "p-3 rounded-full transition-all duration-300",
              newMessage.trim()
                ? "bg-blue-500 text-white hover:bg-blue-600 shadow"
                : "bg-gray-200 text-gray-400 cursor-not-allowed"
            )}
          >
            <FiSend />
          </button>
        </div>
      </div>

      <ToastContainer position="top-right" autoClose={4000} />
    </div>
  );
}
