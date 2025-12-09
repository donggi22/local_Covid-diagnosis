import React from 'react';
import { formatDateKorean, extractTime } from '../../utils/timeCalculations';

/**
 * 다가오는 일정 목록 컴포넌트
 */
const UpcomingEvents = ({ events, onEventClick, onAddClick }) => {
  const typeIcons = {
    surgery: '🏥',
    appointment: '💊',
    xray: '📸'
  };

  const typeColors = {
    surgery: 'bg-red-100 text-red-700 border-red-300',      // 수술: 빨간색
    appointment: 'bg-blue-100 text-blue-700 border-blue-300', // 진료: 파란색
    xray: 'bg-yellow-100 text-yellow-700 border-yellow-300'   // X-Ray 검토: 노란색
  };

  const priorityColors = {
    high: 'bg-red-500',
    medium: 'bg-yellow-500',
    low: 'bg-green-500'
  };

  const getStatusBadge = (event) => {
    if (event.status === 'needs-review') {
      return (
        <span className="text-[10px] px-1.5 py-0.5 bg-red-100 text-red-700 rounded-full">
          ⚠️ X-Ray 재검토 필요
        </span>
      );
    }
    if (event.status === 'scheduled') {
      // 알림 예정 로직 (30분 전 등)
      return (
        <span className="text-[10px] px-1.5 py-0.5 bg-blue-100 text-blue-700 rounded-full">
          🔔 30분 전 알림 예정
        </span>
      );
    }
    return null;
  };

  const formatEventDate = (dateString) => {
    const date = new Date(dateString);
    const days = ['일', '월', '화', '수', '목', '금', '토'];
    const month = date.getMonth() + 1;
    const day = date.getDate();
    const dayOfWeek = days[date.getDay()];
    return `${month}/${day} (${dayOfWeek})`;
  };

  if (events.length === 0) {
    return (
      <div style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)',
        padding: '16px',
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        minHeight: '412px',
        maxHeight: '412px'
      }}>
        <h3 style={{ fontSize: '16px', fontWeight: 600, color: '#1f2937', marginBottom: '4px' }}>
          🔜 다가오는 일정
        </h3>
        <p style={{ fontSize: '12px', color: '#6b7280', marginBottom: '12px' }}>다음 7일</p>
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '32px 0',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '40px', marginBottom: '12px' }}>📅</div>
          <p style={{ fontSize: '14px', color: '#6b7280', marginBottom: '16px' }}>
            예정된 일정이 없습니다
          </p>
          <button
            onClick={onAddClick}
            className="btn btn-primary"
            style={{ fontSize: '14px' }}
          >
            일정 추가하기
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      backgroundColor: 'white',
      borderRadius: '12px',
      boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)',
      padding: '16px',
      flex: 1,
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden',
      minHeight: '412px',
      maxHeight: '412px'
    }}>
      <h3 style={{ fontSize: '16px', fontWeight: 600, color: '#1f2937', marginBottom: '4px' }}>
        🔜 다가오는 일정
      </h3>
      <p style={{ fontSize: '12px', color: '#6b7280', marginBottom: '12px' }}>다음 7일</p>
      <ul style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
        flex: 1,
        overflowY: 'auto'
      }}>
        {events.slice(0, 10).map((event) => (
          <li
            key={event.id}
            style={{
              padding: '8px',
              borderRadius: '6px',
              backgroundColor: 'white',
              border: '1px solid #e5e7eb',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.backgroundColor = '#f9fafb';
              e.currentTarget.style.borderColor = '#4f46e5';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.backgroundColor = 'white';
              e.currentTarget.style.borderColor = '#e5e7eb';
            }}
            onClick={() => onEventClick?.(event)}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              {/* 날짜 + 아이콘 */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '4px 8px',
                borderRadius: '6px',
                fontSize: '11px',
                fontWeight: 600,
                backgroundColor: '#eff6ff',
                color: '#2563eb',
                flexShrink: 0,
                minWidth: '70px'
              }}>
                <span style={{ fontSize: '13px' }}>{typeIcons[event.type] || '📅'}</span>
                <span>{formatEventDate(event.startDateTime)}</span>
              </div>

              <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', gap: '2px' }}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}>
                  <span style={{
                    fontWeight: 600,
                    fontSize: '13px',
                    color: '#1f2937',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap'
                  }}>
                    {event.patient?.name || '환자 정보 없음'}
                  </span>
                  <div
                    style={{
                      width: '6px',
                      height: '6px',
                      borderRadius: '50%',
                      backgroundColor: event.priority === 'high' ? '#ef4444' :
                                      event.priority === 'low' ? '#10b981' : '#f59e0b',
                      flexShrink: 0
                    }}
                    title={`우선순위: ${event.priority || 'medium'}`}
                  />
                </div>

                <div style={{
                  fontSize: '11px',
                  color: '#6b7280'
                }}>
                  {extractTime(event.startDateTime)} - {extractTime(event.endDateTime)}
                </div>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default UpcomingEvents;

