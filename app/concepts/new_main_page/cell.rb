class NewMainPage::Cell < Application::Cell
  private

  def topics
    [
      PageTopic.new(
        title: "بلدة شعث البقاعية نزف اليكم الشهيد الزينبي أحمد علي الحاج حسن \"أبومحمد\"",
        source_name: "إقليم عدن الإخباري",
        category_name: "اقتصاد",
        number_of_votes: 0,
        published_at: 5.minutes.ago,
        description: "﷽ ۞ مِّنَ ٱلْمُؤْمِنِينَ رِجَالٌ صَدَقُواْ مَا عَاهَدُواْ ٱللَّهَ عَلَيْهِ فَمِنْهُمْ مَّن قَضَىٰ نَحْبَهُ وَمِنْهُمْ مَّن يَنتَظِرُ وما بدَّلوا تبديلا ۞ صَدَقَ اللهُ الْعَلِيُّ الْعَظِيْمُ بمزيد من الفخر و الإعتِزاز تزُفُّ بلدة شعث البقاعية (سكان الاوزاعي في الضاحية الجنوبية) أمير من أُمرائها و فارساً من فُرسانها و الّذي ضحّى بنفسه دفاعاً و ذوداً عن المُقدّسات .. […]",
        image_url: "https://scontent.xx.fbcdn.net/v/t39.2147-6/c115.0.130.130/p130x130/20204855_1554565451284713_6561925947648376832_n.jpg?oh=044abaa5230f7ad6c8e98819635b496e&oe=59EEE54F"
      ),
      PageTopic.new(
        title: "صدور قرار جمهوري بتعيين محافظاً لمحافظة البيضاء",
        source_name: "إقليمي",
        category_name: "إقليمي",
        number_of_votes: 12,
        published_at: 23.hours.ago,
        description: "",
        image_url: ""
      ),
      PageTopic.new(
        title: "جريدة ( الرياض ) السعودية : عدن.. تضع أكبر لوحة لأمير الشباب العربي",
        source_name: "عربي برس",
        category_name: "محلي",
        number_of_votes: 42,
        published_at: 2.days.ago,
        description: "أزاحت حملة \"شكرا مملكة الحزم\" و\"شكرا إمارات الخير\"، الستار عن لوحة كبرى لصاحب السمو الملكي الأمير محمد بن سلمان آل سعود ولي ولي العهد، والذي لقب بـ \"أمير الشباب العربي\".",
        image_url: "https://scontent.xx.fbcdn.net/v/t15.0-10/s130x130/20535622_1554599977947927_6952633019416969216_n.jpg?oh=4d2e7b56f1c11f3a64a37ccebe787cbd&oe=5A32BD7A"
      )
    ]
  end
end

class PageTopic
  def initialize(params)
    @params = params.with_indifferent_access
  end

  def method_missing(name)
    @params[name.to_sym]
  end
end
