require "rails_helper"

describe RSSParserService do
  describe "#call" do
    let(:source) { create(:source) }

    it "rss perser job" do
      expect(PostsFetcherJob).to have_receive(:perform_later).with(source.id)

      described_class.call
    end
  end
end
