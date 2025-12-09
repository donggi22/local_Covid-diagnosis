import React, { useState, useMemo } from 'react';

/**
 * 미니 캘린더 컴포넌트
 */
const MiniCalendar = ({ currentDate, schedules, onDateSelect, onAddClick }) => {
  const [viewDate, setViewDate] = useState(new Date(currentDate));

  // 현재 월의 날짜 매트릭스 생성
  const monthMatrix = useMemo(() => {
    const year = viewDate.getFullYear();
    const month = viewDate.getMonth();
    const first = new Date(year, month, 1);
    const last = new Date(year, month + 1, 0);
    const firstDay = first.getDay();
    const totalDays = last.getDate();
    const prevLast = new Date(year, month, 0).getDate();

    const cells = [];

    // 이전 달 날짜
    for (let i = 0; i < firstDay; i++) {
      cells.push({ day: prevLast - (firstDay - 1 - i), other: true });
    }

    // 이번 달 날짜
    for (let d = 1; d <= totalDays; d++) {
      const date = new Date(year, month, d);
      const isToday =
        date.getDate() === new Date().getDate() &&
        date.getMonth() === new Date().getMonth() &&
        date.getFullYear() === new Date().getFullYear();
      const isSelected =
        date.getDate() === currentDate.getDate() &&
        date.getMonth() === currentDate.getMonth() &&
        date.getFullYear() === currentDate.getFullYear();

      // 해당 날짜의 일정 확인
      const daySchedules = schedules.filter((schedule) => {
        if (!schedule.startDateTime) return false;
        const scheduleDate = new Date(schedule.startDateTime);
        // 날짜만 비교 (시간 무시)
        return (
          scheduleDate.getDate() === d &&
          scheduleDate.getMonth() === month &&
          scheduleDate.getFullYear() === year
        );
      });

      const scheduleTypes = [...new Set(daySchedules.map((s) => s.type))];

      cells.push({
        day: d,
        other: false,
        today: isToday,
        selected: isSelected,
        scheduleTypes
      });
    }

    // 다음 달 날짜 (주 단위 완성)
    const totalFilled = cells.length;
    const remainder = totalFilled % 7;
    const trailingCount = remainder === 0 ? 0 : 7 - remainder;
    for (let i = 1; i <= trailingCount; i++) {
      cells.push({ day: i, other: true });
    }

    return cells;
  }, [viewDate, currentDate, schedules]);

  const monthLabel = `${viewDate.getFullYear()}년 ${viewDate.getMonth() + 1}월`;

  const handlePreviousMonth = () => {
    setViewDate(new Date(viewDate.getFullYear(), viewDate.getMonth() - 1, 1));
  };

  const handleNextMonth = () => {
    setViewDate(new Date(viewDate.getFullYear(), viewDate.getMonth() + 1, 1));
  };

  const handleDateClick = (cell) => {
    if (!cell.other) {
      const year = viewDate.getFullYear();
      const month = viewDate.getMonth();
      // 시간을 00:00:00으로 명확히 설정 (로컬 시간대)
      const date = new Date(year, month, cell.day, 0, 0, 0, 0);
      onDateSelect?.(date);
    }
  };

  const typeColors = {
    surgery: 'bg-red-500',      // 수술: 빨간색
    appointment: 'bg-blue-500', // 진료: 파란색
    xray: 'bg-yellow-500'       // X-Ray 검토: 노란색
  };

  return (
    <div style={{
      backgroundColor: 'white',
      borderRadius: '12px',
      boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)',
      padding: '16px',
      flexShrink: 0
    }}>
      <div className="flex items-center justify-between mb-3">
        <button
          onClick={handlePreviousMonth}
          style={{
            color: '#6b7280',
            fontSize: '24px',
            fontWeight: 'bold',
            cursor: 'pointer',
            background: 'none',
            border: 'none',
            padding: '4px 8px',
            transition: 'color 0.2s'
          }}
          onMouseOver={(e) => e.target.style.color = '#1f2937'}
          onMouseOut={(e) => e.target.style.color = '#6b7280'}
          aria-label="이전 달"
        >
          ‹
        </button>
        <h3 style={{
          fontSize: '15px',
          fontWeight: 600,
          color: '#1f2937'
        }}>{monthLabel}</h3>
        <button
          onClick={handleNextMonth}
          style={{
            color: '#6b7280',
            fontSize: '24px',
            fontWeight: 'bold',
            cursor: 'pointer',
            background: 'none',
            border: 'none',
            padding: '4px 8px',
            transition: 'color 0.2s'
          }}
          onMouseOver={(e) => e.target.style.color = '#1f2937'}
          onMouseOut={(e) => e.target.style.color = '#6b7280'}
          aria-label="다음 달"
        >
          ›
        </button>
      </div>

      {/* 요일 헤더 */}
      <div className="grid grid-cols-7 gap-0.5 mb-1">
        {['일', '월', '화', '수', '목', '금', '토'].map((day) => (
          <div key={day} className="text-center text-[10px] text-gray-500 font-medium py-0.5">
            {day}
          </div>
        ))}
      </div>

      {/* 날짜 그리드 */}
      <div className="grid grid-cols-7 gap-0.5">
        {monthMatrix.map((cell, idx) => (
          <button
            key={idx}
            onClick={() => handleDateClick(cell)}
            className={`relative h-8 flex flex-col items-center justify-center rounded-md transition-colors ${
              cell.other
                ? 'text-gray-300'
                : cell.today
                ? 'bg-blue-600 text-white font-semibold'
                : cell.selected
                ? 'bg-blue-50 text-blue-700 border-2 border-blue-600'
                : 'text-gray-700 hover:bg-gray-100'
            }`}
            disabled={cell.other}
          >
            <span className="text-[10px]">{cell.day}</span>
            {/* 일정 표시 점들 */}
            {!cell.other && cell.scheduleTypes && cell.scheduleTypes.length > 0 && (
              <div className="flex gap-0.5 mt-0.5">
                {cell.scheduleTypes.slice(0, 3).map((type, typeIdx) => (
                  <div
                    key={typeIdx}
                    className={`w-1 h-1 rounded-full ${typeColors[type] || 'bg-gray-400'}`}
                  />
                ))}
              </div>
            )}
          </button>
        ))}
      </div>

      {/* 일정 추가 버튼 */}
      {onAddClick && (
        <button
          onClick={onAddClick}
          style={{
            width: '100%',
            marginTop: '16px',
            padding: '10px 16px',
            backgroundColor: '#10b981',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '14px',
            fontWeight: 500,
            cursor: 'pointer',
            transition: 'all 0.2s ease',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = '#059669';
            e.currentTarget.style.boxShadow = '0 2px 6px rgba(0, 0, 0, 0.15)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = '#10b981';
            e.currentTarget.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.1)';
          }}
        >
          + 일정 추가
        </button>
      )}
    </div>
  );
};

export default MiniCalendar;

