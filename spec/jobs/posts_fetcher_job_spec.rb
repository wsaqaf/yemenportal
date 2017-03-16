require "rails_helper"

describe PostsFetcherJob do
  subject { described_class.new }
  let(:item) { double(description: "description", link: "link", pubDate: Time.new, title: "title") }
  let(:source) { build(:source, link: "http://www.ruby-lang.org/en/feeds/news.rss") }
  let(:invalid_source) { build(:source, link: "incorrect_source") }

  describe "#perform" do
    it "create new post" do
      allow(Source).to receive(:find).and_return(source)
      allow(RSSParserService).to receive(:fetch_items).and_return([item])

      expect(PostCreaterService).to receive(:add_post).with(item, source)

      subject.perform(15)
    end

    context "raise error" do
      before do
        allow(Source).to receive(:find).and_return(invalid_source)
      end

      it "for nonexistent path(integration)" do
        expect(invalid_source).to receive(:update).with(state: Source.state.incorrect_path)

        subject.perform(15)
      end

      it "for non rss file" do
        allow(RSSParserService).to receive(:fetch_items).and_raise(RSS::NotWellFormedError)

        expect(invalid_source).to receive(:update).with(state: Source.state.incorrect_path)

        subject.perform(15)
      end
    end
  end
end
