from html import escape


def quality_content(intro, lang='tr'):
    en = lang == 'en'
    stages = [('Veri Toplama', 'Tüm Yıl', 'Data Collection', 'Throughout the year'),
              ('Veri Analizi', 'Eylül', 'Data Analysis', 'September'),
              ('İyileştirme Aksiyon Planı', 'Eylül – Ekim', 'Improvement Action Plan', 'September – October'),
              ('Aksiyon Planı Uygulama', 'Tüm Yıl', 'Action Plan Implementation', 'Throughout the year')]
    areas = [('Değerlendirme Süreci', 'Evaluation Process'), ('Değerlendirici Takımı', 'Evaluation Team'),
             ('Ölçütler', 'Standards'), ('Yönetişim Süreçleri', 'Governance Processes'),
             ('Eğitimler', 'Training'), ('Paydaş Katılımı', 'Stakeholder Engagement'), ('Tüm alanlar', 'All areas')]
    timing = [('Her kurumun akreditasyon süreci sonunda', 'At the end of each institution’s accreditation process'),
              ('Her toplantı sonrası', 'After each meeting'), ('Senede 1 Eylül', 'Once a year in September'),
              ('Senede 2 kere Mart ve Eylül', 'Twice a year, in March and September')]
    rows = [
        (0, 'Akreditasyon sürecindeki Kurum Anketi - Değerlendirme Süreci', 'Institution Survey during Accreditation – Evaluation Process', 0),
        (0, 'Değerlendirici Takımı - Değerlendirme Süreci', 'Evaluation Team – Evaluation Process', 0),
        (1, 'Akreditasyon sürecindeki Kurum Anketi - Değerlendirici Takımı', 'Institution Survey during Accreditation – Evaluation Team', 0),
        (1, 'Değerlendiricilerin birbirini değerlendirme anketi', 'Evaluator Peer Assessment Survey', 0),
        (2, 'Akreditasyon sürecindeki Kurum Anketi - Ölçütler', 'Institution Survey during Accreditation – Standards', 0),
        (2, 'Değerlendirici Takımı Anketi - Ölçütler', 'Evaluation Team Survey – Standards', 0),
        (2, 'Tutarlılık Komitesi ve DAK notları', 'Consistency Committee and DAK Notes', 1),
        (2, 'Ölçütlerin ne kadar karşılandığı ile ilgili analiz', 'Analysis of the Extent to Which Standards Are Met', 2),
        (3, 'Tüm komite ve kurulların yıllık geri bildirim anketleri', 'Annual Feedback Surveys of All Committees and Boards', 2),
        (3, 'Tüm komite ve kurulların öz değerlendirme anketleri', 'Self-assessment Surveys of All Committees and Boards', 2),
        (4, 'Tüm komite ve kurulların yıllık geri bildirim anketleri', 'Annual Feedback Surveys of All Committees and Boards', 2),
        (5, 'Tüm komite ve kurulların yıllık geri bildirim anketleri', 'Annual Feedback Surveys of All Committees and Boards', 2),
        (6, 'Danışma Kurulu', 'Advisory Board', 3),
    ]
    cycle_title = 'Continuous Improvement Cycle' if en else 'Sürekli İyileştirme Döngüsü'
    table_title = 'Data and Indicators' if en else 'Veri ve Göstergeler'
    headings = ('Area', 'Indicator / Data Source', 'Data Collection Frequency / Timing') if en else ('Alan', 'Gösterge / Veri Kaynağı', 'Veri Toplama Sıklığı / Zamanlaması')
    cycle = '<section class="quality-cycle" aria-labelledby="quality-cycle-title"><h2 id="quality-cycle-title">'+cycle_title+'</h2><ol class="quality-stages">'
    for i, (tr, tr_time, eng, en_time) in enumerate(stages, 1):
        cycle += f'<li><span class="quality-step" aria-hidden="true">{i:02}</span><strong>{eng if en else tr}</strong><small>{en_time if en else tr_time}</small></li>'
    cycle += '</ol><p class="quality-repeat">'+('The cycle repeats every year.' if en else 'Döngü her yıl tekrarlanır.')+'</p></section>'
    table = '<section class="quality-data" aria-labelledby="quality-data-title"><h2 id="quality-data-title">'+table_title+'</h2><div class="quality-table-scroll" role="region" aria-labelledby="quality-data-title" tabindex="0"><table class="quality-table"><thead><tr>'
    table += ''.join('<th scope="col">'+h+'</th>' for h in headings)+'</tr></thead><tbody>'
    for area, tr, eng, time in rows:
        table += '<tr><th scope="row">'+escape(areas[area][en])+'</th><td>'+escape(eng if en else tr)+'</td><td>'+escape(timing[time][en])+'</td></tr>'
    table += '</tbody></table></div></section>'
    return intro + cycle + table
