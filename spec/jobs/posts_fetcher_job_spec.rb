require "rails_helper"

describe PostsFetcherJob do
  subject { described_class.new }
  let(:item) { instance_double(description: "description", link: "link", pubDate: Time.new, title: "title") }
  let(:feed) { instance_double(:feed, items: [item]) }
  let(:source) { build(:source, link: "http://www.ruby-lang.org/en/feeds/news.rss") }

  describe "#perform" do
    it "create new post" do
      allow(Source).to receive(:find).and_return(source)
      allow(RSS::Parser).to receive(:parse).and_return(feed)

      expect(Post).to have_received(:create).with({ description: "description", link: "link",
        published_at: item.pubDate, title: "title", source: source, category_id: source.category_id })

      subject.perform(15)
    end
  end
end
