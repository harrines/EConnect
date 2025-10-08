import { useState, useEffect } from "react";
import {
  Check,
  FileText,
  X,
  User,
  PlusCircle,
  Upload,
  CheckCircle,
  Clock,
  Trash2,
  Eye,
} from "lucide-react";
import axios from "axios";
import { ipadr } from "../../Utils/Resuse";

export default function HRDocsReview() {
  const [users, setUsers] = useState([]);
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [newDocName, setNewDocName] = useState("");
  const [assignedDocs, setAssignedDocs] = useState({});
  const [reviewUser, setReviewUser] = useState(null);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [loadingAssign, setLoadingAssign] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoadingUsers(true);
      const res = await axios.get(`${ipadr}/get_all_users`);
      const normalizedUsers = res.data.map((u) => ({
        ...u,
        userId: u.id || u._id || u.userId,
      }));
      setUsers(normalizedUsers);
      await Promise.all(
        normalizedUsers.map((user) => fetchAssignedDocs(user.userId))
      );
    } catch (err) {
      console.error("Error fetching users:", err);
    } finally {
      setLoadingUsers(false);
    }
  };

  const fetchAssignedDocs = async (userId) => {
    try {
      const res = await axios.get(`${ipadr}/documents/assigned/${userId}`);
      setAssignedDocs((prev) => ({ ...prev, [userId]: res.data }));
    } catch (err) {
      console.error(`Error fetching docs for user ${userId}:`, err);
    }
  };

  const toggleUserSelection = (userId) => {
    setSelectedUsers((prev) =>
      prev.includes(userId)
        ? prev.filter((id) => id !== userId)
        : [...prev, userId]
    );
  };

  const handleAssignDocument = async () => {
    if (!selectedUsers.length) return alert("Select at least 1 user.");
    if (!newDocName.trim()) return alert("Enter a document name.");
    const docNameTrimmed = newDocName.trim();

    try {
      setLoadingAssign(true);
      await axios.post(`${ipadr}/assign_docs`, {
        userIds: selectedUsers,
        docName: docNameTrimmed,
      });
      await Promise.all(selectedUsers.map((uid) => fetchAssignedDocs(uid)));
      setNewDocName("");
      setSelectedUsers([]);
    } catch (err) {
      console.error(err);
      alert("Failed to assign document");
    } finally {
      setLoadingAssign(false);
    }
  };

  const handleVerify = async (userId, docName) => {
    try {
      await axios.put(`${ipadr}/review_document`, {
        userId,
        docName,
        status: "verified",
        remarks: "Verified by HR",
      });
      fetchAssignedDocs(userId);
    } catch (err) {
      console.error(err);
      alert("Verification failed");
    }
  };

  const handleDelete = async (userId, docName) => {
    try {
      if (!window.confirm(`Are you sure you want to delete "${docName}"?`))
        return;
      await axios.delete(`${ipadr}/assigned_doc_delete`, {
        data: { userId, docName },
      });
      setAssignedDocs((prev) => ({
        ...prev,
        [userId]: (prev[userId] || []).filter((d) => d.docName !== docName),
      }));
    } catch (err) {
      console.error(err);
      alert("Failed to delete document");
    }
  };

  const filteredUsers = users.filter((user) =>
    user.name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filterDocsByStatus = (docs) => {
    if (statusFilter === "all") return docs;
    return docs.filter((doc) => {
      if (statusFilter === "pending") return !doc.fileUrl;
      if (statusFilter === "uploaded")
        return doc.fileUrl && doc.status !== "verified";
      if (statusFilter === "verified") return doc.status === "verified";
      return true;
    });
  };

  return (
    <div className="p-8 bg-gradient-to-br from-white to-blue-50 min-h-[90vh] w-full rounded-xl shadow-sm">
      <h1 className="text-4xl font-bold text-center text-gray-700 mb-6">
        📄 HR Documents Review
      </h1>

      {/* Assign Section */}
      {selectedUsers.length > 0 && (
        <div className="mb-6 flex flex-wrap gap-4 items-center bg-white shadow-md p-4 rounded-xl border border-gray-100">
          <input
            type="text"
            placeholder="Enter document name"
            value={newDocName}
            onChange={(e) => setNewDocName(e.target.value)}
            className="px-3 py-2 border rounded-lg w-72 focus:ring-2 focus:ring-blue-300"
          />
          <button
            onClick={handleAssignDocument}
            disabled={loadingAssign}
            className="px-4 py-2 bg-emerald-500 text-white rounded-lg shadow hover:bg-emerald-600 flex items-center gap-2 transition"
          >
            <PlusCircle size={18} /> {loadingAssign ? "Assigning..." : "Assign"}
          </button>
        </div>
      )}

      {/* Search and Filter */}
      <div className="mb-6 flex flex-col md:flex-row gap-4">
        <input
          type="text"
          placeholder="Search users by name..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="px-3 py-2 border rounded-lg w-full md:w-72 focus:ring-2 focus:ring-blue-300"
        />
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-3 py-2 border rounded-lg w-full md:w-48 focus:ring-2 focus:ring-blue-300"
        >
          <option value="all">All</option>
          <option value="pending">Pending</option>
          <option value="uploaded">Uploaded</option>
          <option value="verified">Verified</option>
        </select>
      </div>

      {/* Users */}
      {loadingUsers ? (
        <p className="text-center text-gray-500">Loading users...</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredUsers.map((user) => {
            const userDocs = filterDocsByStatus(assignedDocs[user.userId] || []);
            return (
              <div
                key={user.userId}
                className="bg-white border border-gray-100 rounded-xl shadow hover:shadow-md p-5 transition-all duration-300"
              >
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-semibold">
                    {user.name?.[0]?.toUpperCase() || <User size={18} />}
                  </div>
                  <div>
                    <p className="font-medium text-gray-700">{user.name}</p>
                    <p className="text-xs text-gray-400">
                      {userDocs.length} Documents
                    </p>
                  </div>
                </div>

                <div className="flex justify-between items-center">
                  <label className="flex items-center gap-2 text-sm text-gray-600">
                    <input
                      type="checkbox"
                      className="rounded text-blue-500"
                      checked={selectedUsers.includes(user.userId)}
                      onChange={() => toggleUserSelection(user.userId)}
                    />
                    Select
                  </label>
                  <button
                    onClick={() => setReviewUser(user)}
                    className="px-3 py-1 bg-blue-500 text-white rounded-lg text-sm hover:bg-blue-600 transition"
                  >
                    Review
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Modal */}
      {reviewUser && (
        <div className="fixed inset-0 bg-black/20 backdrop-blur-sm flex justify-center items-center z-50">
          <div className="bg-white rounded-xl shadow-xl w-11/12 md:w-2/3 lg:w-1/2 p-6 max-h-[80vh] overflow-y-auto relative border border-gray-100">
            <button
              className="absolute top-4 right-4 text-gray-500 hover:text-gray-700"
              onClick={() => setReviewUser(null)}
            >
              <X size={20} />
            </button>
            <h2 className="text-xl font-semibold text-gray-700 mb-4">
              {reviewUser.name} – Assigned Documents
            </h2>

            <table className="w-full text-left border-collapse">
              <thead className="bg-blue-50 sticky top-0">
                <tr className="text-gray-700">
                  <th className="py-2 px-4">Document</th>
                  <th className="py-2 px-4">Status</th>
                  <th className="py-2 px-4">Assigned By</th>
                  <th className="py-2 px-4 text-center">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filterDocsByStatus(assignedDocs[reviewUser.userId] || []).map(
                  (doc) => (
                    <tr
                      key={doc.docName}
                      className="border-b hover:bg-gray-50 transition"
                    >
                      <td className="py-2 px-4 flex items-center gap-2">
                        <FileText size={16} className="text-blue-500" />
                        {doc.docName}
                      </td>
                      <td className="py-2 px-4">
                        {doc.status === "verified" ? (
                          <span className="bg-emerald-100 text-emerald-700 px-2 py-1 rounded-full text-xs flex items-center gap-1 w-fit">
                            <CheckCircle size={12} /> Verified
                          </span>
                        ) : doc.fileUrl ? (
                          <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded-full text-xs flex items-center gap-1 w-fit">
                            <Upload size={12} /> Uploaded
                          </span>
                        ) : (
                          <span className="bg-gray-100 text-gray-600 px-2 py-1 rounded-full text-xs flex items-center gap-1 w-fit">
                            <Clock size={12} /> Pending
                          </span>
                        )}
                      </td>
                      <td className="py-2 px-4 text-gray-500">
                        {doc.assignedBy || "-"}
                      </td>
                      <td className="py-2 px-4 flex justify-center gap-2">
                        {doc.fileUrl && (
                          <a
                            href={`${ipadr}${doc.fileUrl}`}
                            target="_blank"
                            rel="noreferrer"
                            className="text-blue-600 hover:underline text-sm flex items-center gap-1"
                          >
                            <Eye size={14} />
                          </a>
                        )}
                        {doc.fileUrl && doc.status !== "verified" && (
                          <button
                            onClick={() =>
                              handleVerify(reviewUser.userId, doc.docName)
                            }
                            className="px-2 py-1 bg-emerald-100 text-emerald-700 rounded-lg hover:bg-emerald-200 text-xs flex items-center gap-1"
                          >
                            <Check size={14} />
                          </button>
                        )}
                        <button
                          onClick={() =>
                            handleDelete(reviewUser.userId, doc.docName)
                          }
                          className="px-2 py-1 bg-rose-100 text-rose-700 rounded-lg hover:bg-rose-200 text-xs flex items-center gap-1"
                        >
                          <Trash2 size={14} />
                        </button>
                      </td>
                    </tr>
                  )
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
