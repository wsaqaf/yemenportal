require "rails_helper"

describe RSSParserService do
  describe "#call" do
    let(:source) { create(:source) }

    it "rss perser job" do
      expect(PostsFetcherJob).to receive(:perform_later).with(source.id)

      described_class.call
    end
  end

  describe "#fetch_items" do
    let(:rss) { double }
    let(:post) { build(:post) }
    let(:feed) { double(items: [new_item]) }
    let(:feed_2) { double(items: [old_item]) }
    let(:new_item) { double(pubDate: (post.published_at + 1.hour)) }
    let(:old_item) { double(pubDate: (post.published_at - 1.hour)) }

    it "has any post" do
      allow(RSS::Parser).to receive(:parse).with(rss).and_return(feed)
      allow(Post).to receive(:source_posts).with(555).and_return([])

      expect(described_class.fetch_items(rss, 555)).to eql([new_item])
    end

    it "hasn new post" do
      allow(RSS::Parser).to receive(:parse).with(rss).and_return(feed)
      allow(Post).to receive(:source_posts).with(555).and_return([post])

      expect(described_class.fetch_items(rss, 555)).to eql([new_item])
    end

    it "hasn't new post" do
      allow(RSS::Parser).to receive(:parse).with(rss).and_return(feed_2)
      allow(Post).to receive(:source_posts).with(555).and_return([post])

      expect(described_class.fetch_items(rss, 555)).to eql([])
    end
  end
end
