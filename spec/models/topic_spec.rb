require "rails_helper"

RSpec.describe Topic do
  describe "#update_voting_result" do
    it "updates voting_result to received value" do
      topic = Topic.new

      expect(topic).to receive(:update).with(voting_result: 42)

      topic.update_voting_result(42)
    end
  end
end
