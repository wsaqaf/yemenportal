require "rails_helper"

RSpec.describe PostsFetcher::ItemSaver do
  describe "#save!" do
    subject { described_class.new(source: source, item: item).save! }

    let(:source) { instance_double(Source) }
    let(:item) { instance_double(PostsFetcher::FetchedItem) }

    it "creates a post with its topic" do
      expect(PostsFetcher::PostFactory).to receive_message_chain(:new, :create)
      expect(PostsFetcher::TopicFinder).to receive_message_chain(:new, :attach_topic!)
      subject
    end
  end
end
