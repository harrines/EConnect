import React, { useState, useEffect, useRef } from "react";
import {
  FiSend,
  FiPlus,
  FiSearch,
  FiSmile,
  FiChevronLeft,
} from "react-icons/fi";
import { MessageSquare } from "lucide-react";
import { toast } from "react-toastify";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { GroupModal } from "./GroupModal";
import { MessageBubble } from "./MessageBubble";
import { LS } from "../Utils/Resuse";

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [selectedChat, setSelectedChat] = useState(null);
  const [inputMessage, setInputMessage] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [openGroupModal, setOpenGroupModal] = useState(false);
  const [groupName, setGroupName] = useState("");
  const [users, setUsers] = useState([]);
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [replyThread, setReplyThread] = useState(null);
  const [filteredChats, setFilteredChats] = useState([]);
  const messagesEndRef = useRef(null);
  const currentUser = LS.get("user");

  // Fetch users (for group creation)
  useEffect(() => {
    async function fetchUsers() {
      const res = await fetch("/api/users");
      const data = await res.json();
      setUsers(data);
    }
    fetchUsers();
  }, []);

  // Scroll to bottom when messages update
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Handle message send
  const handleSendMessage = () => {
    if (!inputMessage.trim()) return;

    const newMessage = {
      id: Date.now().toString(),
      from_user: currentUser.name,
      text: inputMessage,
      timestamp: new Date().toISOString(),
    };

    setMessages([...messages, newMessage]);
    setInputMessage("");
    toast.success("Message sent!");
  };

  // Toggle user selection in group modal
  const handleUserToggle = (userId) => {
    setSelectedUsers((prev) =>
      prev.includes(userId)
        ? prev.filter((id) => id !== userId)
        : [...prev, userId]
    );
  };

  // Create new group
  const handleCreateGroup = () => {
    if (!groupName.trim() || selectedUsers.length === 0) {
      toast.error("Enter group name and select members");
      return;
    }

    const newGroup = {
      id: Date.now().toString(),
      name: groupName,
      members: selectedUsers,
    };

    // Simulate group creation
    toast.success(`Group "${groupName}" created!`);
    setGroupName("");
    setSelectedUsers([]);
    setOpenGroupModal(false);
  };

  // Reply to a message
  const handleReply = (message) => {
    setReplyThread(message);
  };

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <div className="w-1/4 border-r border-border p-4 flex flex-col">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold">Chats</h2>
          <Button size="sm" onClick={() => setOpenGroupModal(true)}>
            <FiPlus className="mr-1" /> New Group
          </Button>
        </div>

        <div className="relative mb-3">
          <FiSearch className="absolute left-2 top-2.5 text-muted-foreground" />
          <Input
            placeholder="Search chats..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-8"
          />
        </div>

        <ScrollArea className="flex-1">
          <div className="space-y-2">
            {filteredChats.length > 0 ? (
              filteredChats.map((chat) => (
                <div
                  key={chat.id}
                  onClick={() => setSelectedChat(chat)}
                  className={`p-3 rounded-lg cursor-pointer transition ${
                    selectedChat?.id === chat.id
                      ? "bg-muted"
                      : "hover:bg-muted/50"
                  }`}
                >
                  <div className="font-medium">{chat.name}</div>
                  <div className="text-xs text-muted-foreground truncate">
                    Last message preview...
                  </div>
                </div>
              ))
            ) : (
              <div className="text-sm text-muted-foreground text-center mt-10">
                No chats found
              </div>
            )}
          </div>
        </ScrollArea>
      </div>

      {/* Chat area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-border flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setSelectedChat(null)}
              className="sm:hidden"
            >
              <FiChevronLeft />
            </Button>
            <h2 className="font-semibold text-lg">
              {selectedChat ? selectedChat.name : "Select a Chat"}
            </h2>
          </div>
        </div>

        {/* Messages */}
        <ScrollArea className="flex-1 p-4">
          {messages.length === 0 ? (
            <div className="flex justify-center items-center h-full text-muted-foreground">
              Start the conversation...
            </div>
          ) : (
            messages.map((msg) => (
              <MessageBubble
                key={msg.id}
                message={msg}
                isSender={msg.from_user === currentUser.name}
                onReply={() => handleReply(msg)}
                replyCount={Math.floor(Math.random() * 3)} // demo value
              />
            ))
          )}
          <div ref={messagesEndRef} />
        </ScrollArea>

        {/* Reply thread view */}
        {replyThread && (
          <div className="border-t border-border bg-muted/40 p-3 flex items-center justify-between">
            <div className="text-sm text-muted-foreground">
              Replying to <b>{replyThread.from_user}</b>: {replyThread.text}
            </div>
            <Button
              size="sm"
              variant="ghost"
              onClick={() => setReplyThread(null)}
            >
              Cancel
            </Button>
          </div>
        )}

        {/* Message input */}
        <div className="p-4 border-t border-border flex items-center gap-2">
          <FiSmile className="text-muted-foreground" />
          <Input
            placeholder="Type a message..."
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
          />
          <Button onClick={handleSendMessage}>
            <FiSend />
          </Button>
        </div>
      </div>

      {/* Group Creation Modal */}
      <GroupModal
        open={openGroupModal}
        onOpenChange={setOpenGroupModal}
        groupName={groupName}
        onGroupNameChange={setGroupName}
        users={users}
        selectedUsers={selectedUsers}
        onUserToggle={handleUserToggle}
        onCreateGroup={handleCreateGroup}
        currentUserId={currentUser?.id || ""}
      />
    </div>
  );
};

export default Chat;
