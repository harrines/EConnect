import { useState, useEffect, useRef } from "react";
import {
  FiSend,
  FiPlus,
  FiSearch,
  FiSmile,
  FiChevronLeft,
  FiTrash2,
  FiMessageSquare,
} from "react-icons/fi";
import { LS } from "../Utils/Resuse";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import Picker from "emoji-picker-react";

const ipadr = import.meta.env.VITE_API_BASE_URL ;

const formatTime = (isoString, withDate = false) => {
  if (!isoString) return "";
  let date = new Date(isoString);
  if (isNaN(date.getTime())) return isoString;
  return withDate
    ? date.toLocaleString([], { dateStyle: "short", timeStyle: "short" })
    : date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
};

export default function Chat() {
  const [messages, setMessages] = useState({});
  const [newMessage, setNewMessage] = useState("");
  const [activeChat, setActiveChat] = useState({ id: "", name: "", chatId: "", type: "user" });
  const [contacts, setContacts] = useState([]);
  const [unread, setUnread] = useState({});
  const [isConnected, setIsConnected] = useState(false);
  const [onlineUsers, setOnlineUsers] = useState([]);
  const [selectedThread, setSelectedThread] = useState(null);
  const [threadInput, setThreadInput] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const [showThreadEmojiPicker, setShowThreadEmojiPicker] = useState(false);
  const [showGroupModal, setShowGroupModal] = useState(false);
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [groupName, setGroupName] = useState("");
  const [groups, setGroups] = useState([]);

const [editingGroup, setEditingGroup] = useState(null); 
const [showGroupMembers, setShowGroupMembers] = useState(false);
const [currentGroupMembers, setCurrentGroupMembers] = useState([]);
const [currentGroupName, setCurrentGroupName] = useState("");
const [activeMenu, setActiveMenu] = useState(null);
  const chatEndRef = useRef(null);
  const textareaRef = useRef(null);
  const ws = useRef(null);

  const isManager = LS.get("position");
  const isDepart = LS.get("department");
  const userid = LS.get("userid"); 
  const username = LS.get("username"); 

  const buildChatId = (a, b) => [a, b].sort().join("_");

  // Fetch contacts
  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const res = await fetch(`${ipadr}/get_all_users`);
        const data = await res.json();
        const filtered = data.filter((user) => {
          if (user.id === userid) return false;
          if (isManager?.toLowerCase() === "manager") return true;
          if (isDepart?.toLowerCase() === "hr") return user.position?.toLowerCase() === "manager";
          return user.department?.toLowerCase() !== "hr";
        });
        setContacts(filtered);
      } catch (err) {
        console.error("Failed to fetch users:", err);
      }
    };
    fetchUsers();
  }, [userid, isManager, isDepart]);

  // Fetch groups
  useEffect(() => {
    const fetchGroups = async () => {
      try {
        const res = await fetch(`${ipadr}/get_user_groups/${userid}`);
        const data = await res.json();
        setGroups(data);
      } catch (err) {
        console.error("Failed to fetch groups:", err);
      }
    };
    fetchGroups();
  }, [userid]);

  // Scroll to bottom on new messages
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, activeChat]);

  // WebSocket connection
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
    ws.current.onerror = (err) => {
      console.error("WS error", err);
      setIsConnected(false);
    };

    ws.current.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);

       

        // Thread messages
       if (payload.type === "thread") {
  const threadKey = `thread:${payload.rootId}`;
  setMessages((prev) => {
    const arr = prev[threadKey] || [];
    // Replace if tempId or id exists, else add
    const idx = arr.findIndex((m) => m.tempId === payload.tempId || m.id === payload.id);
    if (idx > -1) {
      arr[idx] = payload; // replace the temp message
      return { ...prev, [threadKey]: [...arr] };
    }
    return { ...prev, [threadKey]: [...arr, payload] };
  });
  return;
}



        // Main chat messages
        const msgChatId =
          payload.chatId ||
          (payload.type === "user"
            ? buildChatId(payload.from_user || payload.from, payload.to_user || payload.to)
            : payload.chatId);

        setMessages((prev) => {
          const chatMessages = prev[msgChatId] || [];
          const filtered = chatMessages.filter((m) => m.id !== payload.id && m.id !== payload.tempId);
          return { ...prev, [msgChatId]: [...filtered, payload] };
        });

        if (msgChatId !== activeChat.chatId) {
          setUnread((prev) => ({ ...prev, [msgChatId]: (prev[msgChatId] || 0) + 1 }));
          toast.info(
            `New message from ${payload.from_user || payload.from}: ${payload.text ? payload.text.slice(0, 60) : "File"}`,
            { position: "top-right", autoClose: 4000 }
          );
        }
      } catch (err) {
        console.error("Invalid WS payload:", event.data, err);
      }
    };
  };

  // Fetch thread messages
  useEffect(() => {
    if (!selectedThread) return;

    fetch(`${ipadr}/thread/${selectedThread.id}`)
      .then((res) => res.json())
      .then((data) =>
        setMessages((prev) => ({ ...prev, [`thread:${selectedThread.id}`]: data }))
      )
      .catch((err) => console.error("Failed to fetch thread:", err));
  }, [selectedThread]);

  // Contact click
  const handleContactClick = async (contact) => {
    try {
      const res = await fetch(`${ipadr}/get_EmployeeId/${encodeURIComponent(contact.name)}`);
      const data = await res.json();
      const employeeId = data.Employee_ID || data.employee_id || data.EmployeeId;

      if (!employeeId) {
        toast.error(`Failed to get employee ID for ${contact.name}`);
        return;
      }

      const chatId = buildChatId(userid, employeeId);
      setActiveChat({ id: employeeId, name: contact.name, chatId, type: "user" });
      setUnread((prev) => ({ ...prev, [chatId]: 0 }));
      openWebSocket("user");

      const historyRes = await fetch(`${ipadr}/history/${chatId}`);
      if (historyRes.ok) {
        const history = await historyRes.json();
        setMessages((prev) => ({ ...prev, [chatId]: history }));
      }
    } catch (err) {
      console.error("Failed to open chat:", err);
      toast.error("Failed to open chat with this contact.");
    }
  };

  // Group click
  const handleGroupClick = async (group) => {
    setActiveChat({ id: group._id, name: group.name, chatId: group._id, type: "group" });
    setUnread((prev) => ({ ...prev, [group._id]: 0 }));
    openWebSocket("group", group._id);

    try {
      const res = await fetch(`${ipadr}/group_history/${group._id}`);
      if (res.ok) {
        const history = await res.json();
        setMessages((prev) => ({ ...prev, [group._id]: history }));
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleRemoveGroup = async (group) => {
    if (!confirm(`Are you sure you want to delete group "${group.name}"?`)) return;

    try {
      const res = await fetch(`${ipadr}/delete_group/${group._id}`, { method: "DELETE" });
      if (res.ok) {
        setGroups((prev) => prev.filter((g) => g._id !== group._id));
        toast.success("Group deleted successfully");
      } else {
        toast.error("Failed to delete group");
      }
    } catch (err) {
      console.error(err);
      toast.error("Error deleting group");
    }
  };

  // Send main message
  const sendMessage = async () => {
    if (!newMessage.trim()) return;

    const attemptSend = async () => {
      if (!ws.current || ws.current.readyState !== WebSocket.OPEN) {
        setTimeout(attemptSend, 100);
        return;
      }

      const tempId = `temp-${Date.now()}-${Math.random()}`;
      const messageData = {
        id: tempId,
        tempId,
        type: "message",
        from_user: userid,
        to_user: activeChat.type === "user" ? activeChat.id : undefined,
        text: newMessage,
        timestamp: new Date().toISOString(),
        chatId: activeChat.chatId,
      };

      setMessages((prev) => {
        const chatMessages = prev[activeChat.chatId] || [];
        return { ...prev, [activeChat.chatId]: [...chatMessages, messageData] };
      });

      ws.current.send(JSON.stringify(messageData));
      setNewMessage("");
    };

    attemptSend();
  };

  // Send thread message
  const sendThreadMessage = async () => {
    if (!selectedThread || !threadInput.trim()) return;

    if (!ws.current || ws.current.readyState !== WebSocket.OPEN) {
      toast.error("Socket not connected");
      return;
    }

    const tempId = `temp-${Date.now()}`;
  

    const payload = {
      type: "thread",
      id: tempId,
      tempId,
      from_user: userid,
      to_user: 
      activeChat.type === "group"
        ? undefined
        : selectedThread.from_user === userid
        ? selectedThread.to_user
        : selectedThread.from_user,
      text: threadInput.trim(),
      rootId: selectedThread.id,
      chatId: activeChat.chatId,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => {
      const key = `thread:${payload.rootId}`;
      const arr = prev[key] || [];
      return { ...prev, [key]: [...arr, payload] };
    });

    ws.current.send(JSON.stringify(payload));

   

    setThreadInput("");
  };

  const getInitials = (name = "") =>
    name
      .split(" ")
      .map((n) => n[0] || "")
      .join("")
      .toUpperCase()
      .slice(0, 2);

  const activeMessages = Array.isArray(messages[activeChat.chatId])
    ? messages[activeChat.chatId].filter((m) =>
        m.text ? m.text.toLowerCase().includes(searchTerm.toLowerCase()) : true
      )
    : [];

  const filteredContacts = contacts.filter((c) =>
    c.name.toLowerCase().includes(searchTerm.toLowerCase())
  );
  const filteredGroups = groups.filter((g) =>
    g.name.toLowerCase().includes(searchTerm.toLowerCase())
  );
  const validGroupUsers = [
    { id: userid, name: username, position: isManager || "User" },
    ...contacts,
  ];

  const getThreadCount = (msgId) => {
    return (messages[`thread:${msgId}`] || []).length;
  };

  const handleViewMembers = (group) => {
  setCurrentGroupMembers(group.members);
  setCurrentGroupName(group.name);
  setShowGroupMembers(true);
};


  return (
    <div className="flex h-screen w-full overflow-hidden bg-background">
      {/* Sidebar */}
      {/* Sidebar */}
<div className="w-80 bg-gray-100 flex flex-col shadow-lg">
  {/* Header */}
  <div className="p-5 flex justify-between items-center border-b border-gray-300">
    <div className="flex items-center gap-3 text-gray-800 font-bold text-xl">
      <FiMessageSquare className="text-2xl" />
      Messages
    </div>
    {isManager?.toLowerCase() === "manager" && (
      <button
        className="p-2 rounded-full hover:bg-gray-200 transition-all"
        onClick={() => setShowGroupModal(true)}
        title="Create Group"
      >
        <FiPlus className="text-xl" />
      </button>
    )}
  </div>

  {/* Search */}
  <div className="p-4">
    <div className="flex items-center gap-2 bg-white rounded-full px-4 py-2 border border-gray-300 focus-within:ring-2 focus-within:ring-blue-200">
      <FiSearch className="text-gray-500" />
      <input
        type="text"
        placeholder="Search..."
        className="w-full bg-transparent outline-none text-gray-700 text-sm placeholder-gray-400"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
      />
    </div>
  </div>

  {/* Groups */}
<div className="flex-1 overflow-y-auto px-3 space-y-2">
  {filteredGroups.map((group) => {
    const isActiveMenu = activeMenu === group._id;

    return (
      <div
        key={group._id}
        className={`px-3 py-2 rounded-lg cursor-pointer flex items-center justify-between transition-all ${
          activeChat.chatId === group._id ? "bg-gray-200 shadow" : "hover:bg-gray-150"
        }`}
        onClick={() => handleGroupClick(group)}
      >
        <div className="flex items-center gap-3 flex-1 min-w-0">
          <div className="w-10 h-10 rounded-full flex items-center justify-center font-bold bg-gray-400 text-white flex-shrink-0">
            {getInitials(group.name)}
          </div>
          <div className="flex flex-col min-w-0 flex-1">
            <span className="truncate font-medium text-gray-800">{group.name}</span>
            <span className="text-xs text-gray-500 truncate">
              {group.members?.filter((m) => m !== userid).length} members
            </span>
          </div>
        </div>

        {/* More Options Dot Button */}
        <div className="relative">
          <button
            className="p-2 rounded-full hover:bg-gray-200 transition-all"
            onClick={(e) => {
              e.stopPropagation();
              setActiveMenu(isActiveMenu ? null : group._id); // toggle menu
            }}
            title="More Options"
          >
            ⋮
          </button>

          {/* Dropdown Menu */}
          {isActiveMenu && (
            <div className="absolute right-0 top-10 bg-white border shadow-md rounded-md flex flex-col w-36 z-10">
              {isManager?.toLowerCase() === "manager" && (
                <>
                  <button
                    className="px-4 py-2 text-left hover:bg-gray-100"
                    onClick={(e) => {
                      e.stopPropagation();
                      setEditingGroup(group);
                      setGroupName(group.name);
                      setSelectedUsers(group.members || []);
                      setShowGroupModal(true);
                      setActiveMenu(null); // close menu
                    }}
                  >
                    ✏️ 
                  </button>
                  <button
                    className="px-4 py-2 text-left hover:bg-gray-100 flex items-center gap-2"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleRemoveGroup(group);
                      setActiveMenu(null); // close menu
                    }}
                  >
                    <FiTrash2 size={16} /> 
                  </button>
                </>
              )}
              <button
                className="px-4 py-2 text-left hover:bg-gray-100"
                onClick={(e) => {
                  e.stopPropagation();
                  handleViewMembers(group);
                  setActiveMenu(null); 
                }}
              >
                👥
              </button>
            </div>
          )}
        </div>
      </div>
    );
  })}


    {/* Contacts */}
    <div className="px-3 py-2 text-xs text-gray-500 uppercase tracking-wider font-semibold mt-4">
      Contacts
    </div>
    {filteredContacts.map((contact) => {
      const chatId = buildChatId(userid, contact.id);
      const isOnline = onlineUsers.includes(contact.id);
      return (
        <div
          key={contact.id}
          className={`px-3 py-2 rounded-lg cursor-pointer flex items-center justify-between transition-all ${
            activeChat.chatId === chatId
              ? "bg-gray-200 shadow"
              : "hover:bg-gray-150"
          }`}
          onClick={() => handleContactClick(contact)}
        >
          <div className="flex items-center gap-3 flex-1 min-w-0">
            <div className="relative">
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-white shadow ${
                  isOnline ? "bg-green-400" : "bg-gray-400"
                }`}
              >
                {getInitials(contact.name)}
              </div>
              {isOnline && (
                <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 rounded-full border-2 border-white"></div>
              )}
            </div>
            <div className="flex flex-col min-w-0 flex-1">
              <span className="truncate font-medium text-gray-800">
                {contact.name}
              </span>
              <span className="text-xs text-gray-500 truncate">
                {contact.position || ""}
              </span>
            </div>
          </div>
          {unread[chatId] > 0 && (
            <span className="bg-red-100 text-red-700 text-xs px-2 py-0.5 rounded-full font-semibold">
              {unread[chatId]}
            </span>
          )}
        </div>
      );
    })}
  </div>
</div>


      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col bg-background">
        {/* Header */}
        <div className="bg-card border-b border-border px-6 py-4 flex items-center justify-between shadow-sm">
          <div className="flex items-center gap-4">
            {activeChat.id ? (
              <>
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-primary-foreground font-bold text-lg shadow-md">
                  {getInitials(activeChat.name)}
                </div>
                <div>
                  <h1 className="text-lg font-semibold text-foreground">
                    {activeChat.name}
                  </h1>
                  
                </div>
              </>
            ) : (
              <div className="text-muted-foreground"></div>
            )}
          </div>
        </div>
        {!activeChat.id && (
    <div className="flex-1 flex flex-col items-center justify-center bg-gradient-to-b from-white to-white-50 text-center p-6">
      <FiMessageSquare className="text-7xl text-blue-200 mb-6 animate-pulse" />
      <h2 className="text-2xl font-semibold text-gray-800 mb-2">
        Welcome to Chat
      </h2>
      <p className="text-gray-500">
        Select a contact or group from the left sidebar to start messaging.
      </p>
    </div>
  )}

        {/* Messages & Thread */}
<div className="flex flex-1 overflow-hidden">
  {/* Messages */}
  <div className="flex-1 flex flex-col">
    <div className="flex-1 p-6 overflow-y-auto space-y-4 bg-gradient-to-b from-white to-gray-50">
      {activeMessages.map((m) => {
        const isSender = m.from_user === userid;
        const msgId = m.id || m.tempId;
        const threadCount = getThreadCount(msgId);
         // Get the display name
  let displayName = "Unknown";
  if (isSender) {
    displayName = "You";
  } else {
    const contact = contacts.find((c) => c.id === m.from_user);
    displayName = contact ? contact.name : m.from_user; // fallback to ID
  }
        const textHtml = (m.text || "").replace(
          /@(\w+)/g,
          '<span class="text-accent font-semibold">@$1</span>'
        );

        return (
          <div
            key={msgId}
            className={`flex animate-in fade-in slide-in-from-bottom-2 duration-300 ${
              isSender ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`max-w-xl p-4 rounded-2xl break-words shadow-md relative transition-all duration-300 hover:shadow-lg ${
                isSender
                  ? "bg-gradient-to-br from-blue-100 to-blue-200 text-primary-foreground rounded-br-sm"
                  : "bg-gray-100 text-gray-800 rounded-bl-sm border border-gray-200"
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                 <span className="font-medium text-sm">{displayName}</span>
                <span
                  className={`text-xs ${
                    isSender ? "text-primary-foreground/70" : "text-gray-400"
                  }`}
                >
                    {formatTime(m.timestamp)}
                </span>
              </div>

              <div
                className="text-sm leading-relaxed"
                dangerouslySetInnerHTML={{ __html: textHtml }}
              />

              <div className="flex items-center gap-3 mt-3 pt-2 border-t border-current/10">
                <button
                  onClick={() => setSelectedThread(m)}
                  className={`text-xs font-medium hover:underline transition-all flex items-center gap-1 ${
                    isSender
                      ? "text-primary-foreground/80 hover:text-primary-foreground"
                      : "text-gray-500 hover:text-gray-700"
                  }`}
                >
                  <FiMessageSquare size={12} />
                  Reply
                </button>

                {threadCount > 0 && (
                  <div
                    className={`text-xs ml-auto ${
                      isSender ? "text-primary-foreground/70" : "text-gray-400"
                    }`}
                  >
                    {threadCount} {threadCount === 1 ? "reply" : "replies"}
                  </div>
                )}
              </div>
            </div>
          </div>
        );
      })}
      <div ref={chatEndRef}></div>
    </div>
  


            {/* Input */}
            {activeChat.id && (
              <div className="border-t border-border bg-card p-4">
                <div className="flex items-center gap-3 relative">
                  <button
                    className="p-2 rounded-full hover:bg-muted transition-all text-muted-foreground hover:text-foreground"
                    onClick={() => setShowEmojiPicker((prev) => !prev)}
                  >
                    <FiSmile className="text-xl" />
                  </button>
                  {showEmojiPicker && (
                    <div className="absolute bottom-16 left-3 z-50 shadow-xl rounded-lg overflow-hidden">
                      <Picker
                        onEmojiClick={(e) => setNewMessage((prev) => prev + e.emoji)}
                        searchPlaceholder="Search emojis..."
                      />
                    </div>
                  )}
                  <input
                    ref={textareaRef}
                    className="flex-1 px-4 py-2.5 rounded-full border border-border bg-background focus:outline-none focus:ring-2 focus:ring-primary/50 placeholder-muted-foreground text-sm"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    placeholder="Type a message..."
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        sendMessage();
                      }
                    }}
                  />
                  <button
                    onClick={sendMessage}
                    disabled={!newMessage.trim() || !isConnected}
                    className={`p-3 rounded-full transition-all duration-300 ${
                      newMessage.trim() && isConnected
                        ? "bg-gradient-to-r from-primary to-accent text-primary-foreground shadow-lg hover:scale-105"
                        : "bg-muted text-muted-foreground cursor-not-allowed"
                    }`}
                  >
                    <FiSend className="text-lg" />
                  </button>
                </div>
              </div>
            )}
          </div>


{/* Thread Panel */}
{selectedThread && (
  <div className="w-96 bg-gradient-to-b from-white to-gray-50 border-l border-gray-200 flex flex-col shadow-lg">
    {/* Thread Header */}
    <div className="p-4 border-b border-gray-200 flex items-center gap-3 bg-gradient-to-r from-blue-50 to-purple-50">
      <button
        className="p-2 rounded-lg hover:bg-gray-100 transition-all"
        onClick={() => setSelectedThread(null)}
      >
        <FiChevronLeft size={20} />
      </button>
      <div className="flex-1">
        <div className="font-semibold text-gray-800">Thread</div>
        <div className="text-xs text-gray-500">
          {selectedThread.from_user} • {formatTime(selectedThread.timestamp, true)}
        </div>
      </div>
    </div>

    {/* Thread Messages */}
    <div className="flex-1 overflow-y-auto p-4 space-y-3">
      {/* Original Message */}
      <div className="p-4 bg-blue-50/50 rounded-2xl border border-blue-100 shadow-sm">
        <div className="text-xs text-blue-400 mb-2">
          {selectedThread.from_user} • {formatTime(selectedThread.timestamp, true)}
        </div>
        <div className="text-sm text-gray-800">{selectedThread.text}</div>
        <div className="text-xs text-blue-400 mt-2 font-medium">Original message</div>
      </div>

      {/* Thread Replies */}
      {(messages[`thread:${selectedThread.id}`] || []).map((t) => (
        <div
          key={t.id || t.tempId}
          className="p-3 border border-gray-200 rounded-xl bg-white shadow-sm hover:shadow-md transition-shadow"
        >
          <div className="text-xs text-gray-400 mb-2">
            {t.from_user} • {formatTime(t.timestamp, true)}
          </div>
          <div className="text-sm text-gray-800">{t.text}</div>
        </div>
      ))}
    </div>

    {/* Thread Input */}
    <div className="border-t border-gray-200 bg-white p-4">
      <div className="flex items-center gap-2 relative">
        <button
          className="p-2 rounded-full hover:bg-gray-100 transition-all text-gray-400 hover:text-gray-700"
          onClick={() => setShowThreadEmojiPicker((prev) => !prev)}
        >
          <FiSmile size={18} />
        </button>
        {showThreadEmojiPicker && (
          <div className="absolute bottom-16 left-0 z-50 shadow-xl rounded-lg overflow-hidden">
            <Picker
              onEmojiClick={(e) => setThreadInput((prev) => prev + e.emoji)}
              searchPlaceholder="Search emojis..."
            />
          </div>
        )}
        <input
          value={threadInput}
          onChange={(e) => setThreadInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              sendThreadMessage();
            }
          }}
          placeholder="Reply in thread..."
          className="flex-1 px-3 py-2 rounded-full border border-gray-200 bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-200 text-sm placeholder-gray-400"
        />
        <button
          onClick={sendThreadMessage}
          disabled={!threadInput.trim() || !isConnected}
          className={`p-2.5 rounded-full transition-all ${
            threadInput.trim() && isConnected
              ? "bg-blue-500 text-white hover:bg-blue-600"
              : "bg-gray-200 text-gray-400 cursor-not-allowed"
          }`}
        >
          <FiSend size={16} />
        </button>
      </div>
    </div>
  </div>
)}

        </div>
      </div>

      {/* Group Modal */}
{showGroupModal && (
  <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex justify-center items-center z-50">
    <div className="bg-gradient-to-b from-white to-gray-50 p-6 rounded-2xl w-96 shadow-2xl border border-gray-200">
      <h2 className="text-xl font-bold mb-4 text-gray-800">
        {editingGroup ? "Edit Group" : "Create Group"}
      </h2>

      <input
        type="text"
        placeholder="Group Name"
        className="w-full border border-gray-200 bg-gray-50 rounded-lg px-4 py-2.5 mb-4 focus:outline-none focus:ring-2 focus:ring-blue-200 text-gray-800 placeholder-gray-400"
        value={groupName}
        onChange={(e) => setGroupName(e.target.value)}
      />

      <div className="max-h-64 overflow-y-auto border border-gray-200 rounded-lg p-3 mb-4 space-y-2 bg-blue-50/30">
        {validGroupUsers.map((user) => (
          <label
            key={user.id}
            className="flex items-center gap-3 cursor-pointer p-2 rounded-lg hover:bg-blue-50 transition-colors"
          >
            <input
              type="checkbox"
              value={user.id}
              checked={selectedUsers.includes(user.id)}
              onChange={(e) => {
                const uid = e.target.value;
                setSelectedUsers((prev) =>
                  prev.includes(uid) ? prev.filter((id) => id !== uid) : [...prev, uid]
                );
              }}
              className="w-4 h-4 text-blue-500 border-gray-300 rounded focus:ring-blue-200"
            />
            <span className="text-gray-800">
              {user.name} {user.id === userid && <span className="text-gray-500 text-xs">(You)</span>}
            </span>
          </label>
        ))}
      </div>

      <div className="flex justify-end gap-3">
        <button
          className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          onClick={() => {
            setShowGroupModal(false);
            setGroupName("");
            setSelectedUsers([]);
            setEditingGroup(null);
          }}
        >
          Cancel
        </button>
        <button
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors shadow-md"
          onClick={async () => {
            const validMembers = Array.from(new Set([...selectedUsers.filter((id) => id), userid]));
            if (!groupName.trim() || validMembers.length === 0) {
              toast.error("Enter group name and select valid users");
              return;
            }

            try {
              if (editingGroup) {
                // Update group
                const res = await fetch(`${ipadr}/update_group/${editingGroup._id}`, {
                  method: "PUT",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ name: groupName, members: validMembers }),
                });
                const data = await res.json();
                if (res.ok) {
                  setGroups((prev) =>
                    prev.map((g) => (g._id === editingGroup._id ? { ...g, name: groupName, members: validMembers } : g))
                  );
                  toast.success("Group updated!");
                } else toast.error(data?.detail || "Failed to update group");
              } else {
                // Create new group
                const res = await fetch(`${ipadr}/create_group`, {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ name: groupName, members: validMembers }),
                });
                const data = await res.json();
                if (res.ok || data.status === "success") {
                  setGroups((prev) => [...prev, { _id: data.group_id, name: groupName, members: validMembers }]);
                  toast.success("Group created!");
                } else toast.error("Failed to create group");
              }

              setShowGroupModal(false);
              setGroupName("");
              setSelectedUsers([]);
              setEditingGroup(null);
            } catch (err) {
              console.error(err);
              toast.error("Error saving group");
            }
          }}
        >
          {editingGroup ? "Save" : "Create"}
        </button>
      </div>
    </div>
  </div>
)}

{showGroupMembers && (
  <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex justify-center items-center z-50">
    <div className="bg-white p-6 rounded-2xl w-80 shadow-2xl border border-gray-200">
      <h2 className="text-xl font-bold mb-4 text-gray-800">
        Members of "{currentGroupName}"
      </h2>

      <ul className="space-y-2 max-h-64 overflow-y-auto">
        {currentGroupMembers.map((memberId) => {
          const user = validGroupUsers.find((u) => u.id === memberId);
          return (
            <li key={memberId} className="text-gray-800">
              {user ? user.name : memberId}
              {memberId === userid && <span className="text-gray-500 text-xs"> (You)</span>}
            </li>
          );
        })}
      </ul>

      <div className="flex justify-end mt-4">
        <button
          className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          onClick={() => setShowGroupMembers(false)}
        >
          Close
        </button>
      </div>
    </div>
  </div>
)}




      <ToastContainer position="top-right" autoClose={4000} />
    </div>
  );
}