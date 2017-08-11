require "rails_helper"

describe Flag do
  describe ".include_number_of_reviews_for_topic" do
    it "adds number_of_reviews_for_topic with correct value to Flag instances" do
      user = create(:user)
      topic = create(:topic)
      another_topic = create(:topic)
      flag = Flag.create
      Review.create(moderator: user, topic: topic, flag: flag)
      Review.create(moderator: user, topic: another_topic, flag: flag)

      flags = Flag.include_number_of_reviews_for_topic(topic)

      expect(flags.first.number_of_reviews_for_topic).to eq(1)
    end
  end

  describe ".include_topic_reviwed_by_user" do
    it "adds topic_reviewed_by_user with correct boolean value to Flag instances" do
      user = create(:user)
      topic = create(:topic)
      another_topic = create(:topic)
      flag = Flag.create
      Review.create(moderator: user, topic: topic, flag: flag)

      flag = Flag.include_topic_reviewed_by_user(topic, user).first
      another_topic_flag = Flag.include_topic_reviewed_by_user(another_topic, user).first

      expect(flag.topic_reviewed_by_user?).to eq(true)
      expect(another_topic_flag.topic_reviewed_by_user?).to eq(false)
    end
  end

  describe "#number_of_reviews_for_topic" do
    it "equals 0 when topic is not specified" do
      expect(Flag.new.number_of_reviews_for_topic).to eq(0)
    end
  end

  describe "#topic_reviewed_by_user?" do
    it "equals false when topic and user aren't specified" do
      expect(Flag.new.topic_reviewed_by_user?).to eq(false)
    end
  end
end
