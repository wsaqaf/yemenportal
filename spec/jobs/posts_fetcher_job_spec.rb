require "rails_helper"

describe PostsFetcherJob do
  subject { described_class.new }
  let(:item) { double(description: "description", link: "link", pubDate: Time.new, title: "title") }
  let(:source) { build(:source, link: "http://www.ruby-lang.org/en/feeds/news.rss") }
  let(:facebbok_source) { build(:source, link: "https://www.facebook.com/facebook", source_type: :facebook) }
  let(:invalid_source) { build(:source, link: "http://www.ruby-lang.org") }

  describe "#perform" do
    it "create new rss post", slow: true do
      allow(Source).to receive(:find).and_return(source)
      allow(RSSParserService).to receive(:fetch_items).and_return([item])

      expect(PostCreaterService).to receive(:add_post).with(item, source)

      subject.perform(15)
    end

    it "create new facebook post", slow: true do
      allow(Source).to receive(:find).and_return(facebbok_source)
      allow(RSSParserService).to receive(:fetch_facebook_items).and_return([item])

      expect(PostCreaterService).to receive(:add_post).with(item, facebbok_source)

      subject.perform(15)
    end

    context "raise error" do
      it "for nonexistent path(integration)" do
        allow(Source).to receive(:find).and_return(invalid_source)
        allow(RSSParserService).to receive(:fetch_items).and_raise(Errno::ENOENT)
        expect(invalid_source).to receive(:update).with(state: Source.state.incorrect_path)

        subject.perform(15)
      end

      it "for non rss file" do
        allow(Source).to receive(:find).and_return(source)
        allow(RSSParserService).to receive(:fetch_items).and_raise(RSS::NotWellFormedError)

        expect(source).to receive(:update).with(state: Source.state.incorrect_stucture)

        subject.perform(15)
      end
    end
  end
end
