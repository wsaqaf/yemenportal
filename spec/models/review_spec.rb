require "rails_helper"

describe Review do
  describe ".with_resolve_flag" do
    let(:moderator) { create(:user_moderator) }
    let(:topic) { create(:topic) }

    it "returns empty array if there is no review with resolve flag" do
      flag = create(:flag)
      Review.create(moderator: moderator, topic: topic, flag: flag)

      expect(Review.with_resolve_flag(topic, moderator)).to be_empty
    end

    it "returns an array with one review with resolve flag" do
      flag = create(:resolve_flag)
      review = Review.create(moderator: moderator, topic: topic, flag: flag)

      expect(Review.with_resolve_flag(topic, moderator)).to include(review)
    end
  end
end
