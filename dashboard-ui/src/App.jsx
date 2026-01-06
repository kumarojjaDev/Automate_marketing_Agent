import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Mail, Users, CheckCircle, Search, Clock, ExternalLink, X, Linkedin } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const Modal = ({ isOpen, onClose, title, children }) => {
    if (!isOpen) return null;
    return (
        <div className="modal-overlay" onClick={onClose}>
            <motion.div
                className="modal-content"
                onClick={e => e.stopPropagation()}
                initial={{ opacity: 0, scale: 0.8, y: 50 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.8, y: 50 }}
                transition={{ type: "spring", damping: 25, stiffness: 300 }}
            >
                <div className="modal-header">
                    <h3 className="modal-title">{title}</h3>
                    <button className="modal-close-btn" onClick={onClose}>
                        <X size={20} />
                    </button>
                </div>
                <div className="modal-body">
                    {children}
                </div>
            </motion.div>
        </div>
    );
};

const App = () => {
    const [leads, setLeads] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedEmail, setSelectedEmail] = useState(null);

    const fetchLeads = async () => {
        try {
            const response = await axios.get('http://localhost:3001/api/leads');
            setLeads(response.data);
            setLoading(false);
        } catch (error) {
            console.error('Error fetching leads:', error);
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchLeads();
        const interval = setInterval(fetchLeads, 10000); // Polling every 10s for snappier updates
        return () => clearInterval(interval);
    }, []);

    const stats = [
        { label: 'Total Leads', value: leads.length, icon: Users, color: 'var(--accent-blue)' },
        { label: 'Emails Sent', value: leads.filter(l => l.status === 'SENT').length, icon: CheckCircle, color: 'var(--success)' },
        { label: 'Researching', value: leads.filter(l => l.status === 'RESEARCHING').length, icon: Search, color: 'var(--pending)' },
        { label: 'Pending', value: leads.filter(l => !l.status || l.status === 'NEW').length, icon: Clock, color: 'var(--text-secondary)' },
    ];

    return (
        <div className="dashboard-container">
            <header className="header">
                <div className="brand">
                    <h1>LeadPulse AI</h1>
                </div>
                <div className="last-updated">
                    <p className="text-dim">
                        Live Feed • Updating every 10s
                    </p>
                </div>
            </header>

            <div className="stats-grid">
                {stats.map((stat, i) => (
                    <motion.div
                        key={stat.label}
                        className="stat-card"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.1 }}
                    >
                        <div className="stat-label">{stat.label}</div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <div className="stat-value">{stat.value}</div>
                            <stat.icon size={24} color={stat.color} />
                        </div>
                    </motion.div>
                ))}
            </div>

            <div className="leads-table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Lead</th>
                            <th>Company / Role</th>
                            <th>Research</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {leads.map((lead, i) => (
                            <motion.tr
                                key={lead.lead_id || i}
                                initial={{ x: -50, opacity: 0 }}
                                animate={{ x: 0, opacity: 1 }}
                                transition={{
                                    delay: i * 0.1,
                                    type: "spring",
                                    stiffness: 100,
                                    damping: 10
                                }}
                                whileHover={{ scale: 1.01, backgroundColor: "rgba(255,255,255,0.03)" }}
                            >
                                <td>
                                    <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                                        {lead.first_name} {lead.last_name}
                                    </div>
                                    <div className="text-dim">{lead.email}</div>
                                    {lead.linkedin_url && (
                                        <a href={lead.linkedin_url} target="_blank" rel="noreferrer" className="link-website" style={{ marginTop: '0.25rem' }}>
                                            <Linkedin size={12} /> LinkedIn Profile
                                        </a>
                                    )}
                                </td>
                                <td>
                                    <div style={{ fontWeight: 500 }}>{lead.company_name}</div>
                                    <a href={lead.company_website} target="_blank" rel="noreferrer" className="link-website">
                                        {lead.company_website ? lead.company_website.replace('https://', '').split('/')[0] : 'No Website'} <ExternalLink size={10} />
                                    </a>
                                    <div className="text-dim" style={{ marginTop: '0.25rem', fontSize: '0.8rem' }}>
                                        {lead.role || 'Role Unknown'}
                                    </div>
                                </td>
                                <td>
                                    {lead.linkedin_post ? (
                                        <div title={lead.linkedin_post}>
                                            <div style={{ fontSize: '0.75rem', color: 'var(--accent-cyan)', marginBottom: '4px', fontWeight: 600 }}>RECENT POST FOUND</div>
                                            <div className="truncate" style={{ maxWidth: '250px', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                                                "{lead.linkedin_post}"
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="text-dim" style={{ fontSize: '0.8rem' }}>
                                            <em>Fallback to Web Research</em>
                                        </div>
                                    )}
                                </td>
                                <td>
                                    <span className={`status-badge status-${(lead.status || 'NEW').toLowerCase()}`}>
                                        {lead.status || 'NEW'}
                                    </span>
                                    {lead.status_note && (
                                        <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', marginTop: '4px', maxWidth: '150px' }}>
                                            {lead.status_note}
                                        </div>
                                    )}
                                </td>
                                <td>
                                    {lead.email_subject ? (
                                        <button
                                            className="view-draft-btn"
                                            onClick={() => setSelectedEmail(lead)}
                                        >
                                            <Mail size={14} style={{ marginRight: '6px', verticalAlign: 'text-bottom' }} />
                                            View Draft
                                        </button>
                                    ) : (
                                        <span className="text-dim">-</span>
                                    )}
                                </td>
                            </motion.tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <AnimatePresence>
                {selectedEmail && (
                    <Modal
                        isOpen={!!selectedEmail}
                        onClose={() => setSelectedEmail(null)}
                        title={`Email to ${selectedEmail.first_name}`}
                    >
                        <div style={{ marginBottom: '1.5rem' }}>
                            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>SUBJECT</div>
                            <div style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                                {selectedEmail.email_subject}
                            </div>
                        </div>
                        <div>
                            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>BODY CONTENT</div>
                            <div className="email-preview-box">
                                {selectedEmail.email_body}
                            </div>
                        </div>
                    </Modal>
                )}
            </AnimatePresence>
        </div>
    );
};

export default App;
