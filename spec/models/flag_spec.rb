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

  describe "#number_of_reviews_for_topic" do
    it "equals 0 when topic is not specified" do
      expect(Flag.new.number_of_reviews_for_topic).to eq(0)
    end
  end
end
