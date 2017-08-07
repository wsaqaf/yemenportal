require "rails_helper"

RSpec.describe Topic do
  describe ".include_voted_by_user" do
    it "returns topics with upvoted_by_user and downvoted_by_user attributes" do
      user = create(:user)
      topic_voted_by_user = create(:topic)
      Vote.create(topic: topic_voted_by_user, user: user, value: 1)

      another_user = create(:user)
      topic_not_voted_by_user = create(:topic)
      Vote.create(topic: topic_voted_by_user, user: another_user, value: 1)
      Vote.create(topic: topic_not_voted_by_user, user: another_user, value: 1)

      topic_downvoted_by_user = create(:topic)
      Vote.create(topic: topic_downvoted_by_user, user: user, value: -1)

      topics = Topic.include_voted_by_user(user)

      expect(topics.first.upvoted_by_user?).to eq(true)
      expect(topics.second.upvoted_by_user?).to eq(false)
      expect(topics.third.downvoted_by_user?).to eq(true)
    end
  end

  describe "#update_voting_result" do
    it "updates voting_result to received value" do
      topic = Topic.new

      expect(topic).to receive(:update).with(voting_result: 42)

      topic.update_voting_result(42)
    end
  end
end
