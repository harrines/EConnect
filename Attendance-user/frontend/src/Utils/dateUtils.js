  return (
    <div
      className={cn(
        "flex mb-4 animate-fade-in",
        isSender ? "justify-end" : "justify-start"
      )}
    >
      <div
        className={cn(
          "max-w-md px-4 py-3 rounded-2xl shadow-soft transition-all hover:shadow-medium",
          isSender
            ? "bg-gradient-primary text-primary-foreground rounded-br-md"
            : "bg-card text-card-foreground rounded-bl-md border border-border"
        )}
      >
        <div className="flex items-center gap-2 mb-1">
          <span className="text-xs font-semibold opacity-90">
            {isSender ? "You" : message.from_user}
          </span>
          <span className={cn("text-xs opacity-70", isSender ? "text-primary-foreground" : "text-muted-foreground")}>
            {formatTime(message.timestamp)}
          </span>
        </div>
        <div
          className="text-sm leading-relaxed break-words"
          dangerouslySetInnerHTML={{ __html: processText(message.text) }}
        />
        <div className="flex items-center gap-2 mt-2 pt-2 border-t border-white/20">
          <Button
            variant="ghost"
            size="sm"
            onClick={onReply}
            className={cn(
              "h-7 px-2 text-xs gap-1",
              isSender
                ? "text-primary-foreground hover:bg-white/20"
                : "text-muted-foreground hover:bg-secondary"
            )}
          >
            <MessageSquare className="w-3 h-3" />
            Reply
          </Button>
          {replyCount > 0 && (
            <span className={cn("text-xs", isSender ? "text-primary-foreground/70" : "text-muted-foreground")}>
              {replyCount} {replyCount === 1 ? "reply" : "replies"}
            </span>



this i needed so replace this cod ein this