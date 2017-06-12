require "rails_helper"

describe RSSParserService do
  let(:source) { create(:source, id: 555) }

  describe "#call" do
    it "rss perser job" do
      expect(PostsFetcherJob).to receive(:perform_later).with(source.id)

      described_class.call
    end
  end

  describe "#fetch_items" do
    let(:rss) { double }
    let(:post) { build(:post) }
    let(:feed) { double(entries: [new_item]) }
    let(:feed_2) { double(entries: [old_item]) }
    let(:new_item) { double(published: (post.published_at + 1.hour)) }
    let(:old_item) { double(published: (post.published_at - 1.hour)) }

    it "has any post" do
      allow(Feedjira::Feed).to receive(:parse).and_return(feed)
      allow(Post).to receive(:source_posts).with(555).and_return([])

      expect(described_class.fetch_items(source)).to eql([new_item])
    end

    it "has new post" do
      allow(Feedjira::Feed).to receive(:parse).and_return(feed)
      allow(Post).to receive(:source_posts).with(555).and_return([post])

      expect(described_class.fetch_items(source)).to eql([new_item])
    end

    it "hasn't new post" do
      allow(Feedjira::Feed).to receive(:parse).and_return(feed_2)
      allow(Post).to receive(:source_posts).with(555).and_return([post])

      expect(described_class.fetch_items(source)).to eql([])
    end
  end

  describe "#fetch_facebook_items" do
    let(:fb_source) { create(:source, link: "https://www.facebook.com/facebook", source_type: :facebook) }
    let(:post) { build(:post) }
    let(:connection) { double }
    let(:new_item) { { "created_time" => (post.published_at + 1.hour).to_s } }
    let(:old_item) { { "created_time" => (post.published_at - 1.hour).to_s } }

    it "has any post" do
      allow(Koala::Facebook::API).to receive(:new).and_return(connection)
      allow(Post).to receive(:source_posts).and_return([])
      allow(connection).to receive(:get_connection).with("facebook", "posts").and_return([new_item])

      expect(described_class.fetch_facebook_items(fb_source)).to eql([new_item])
    end

    it "has new post" do
      allow(Koala::Facebook::API).to receive(:new).and_return(connection)
      allow(Post).to receive(:source_posts).and_return([post])
      allow(connection).to receive(:get_connection).with("facebook", "posts").and_return([new_item])

      expect(described_class.fetch_facebook_items(fb_source)).to eql([new_item])
    end

    it "hasn't new post" do
      allow(Koala::Facebook::API).to receive(:new).and_return(connection)
      allow(Post).to receive(:source_posts).and_return([post])
      allow(connection).to receive(:get_connection).with("facebook", "posts").and_return([old_item])

      expect(described_class.fetch_facebook_items(fb_source)).to eql([])
    end
  end
end
