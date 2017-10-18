require "rails_helper"

describe Flag do
  describe ".include_number_of_reviews_for_post" do
    it "adds number_of_reviews_for_posr with correct value to Flag instances" do
      user = create(:user)
      post = create(:post)
      another_post = create(:post)
      flag = Flag.create
      Review.create(moderator: user, post: post, flag: flag)
      Review.create(moderator: user, post: another_post, flag: flag)

      flags = Flag.include_number_of_reviews_for_post(post)

      expect(flags.first.number_of_reviews_for_post).to eq(1)
    end
  end

  describe "#number_of_reviews_for_post" do
    it "equals 0 when post is not specified" do
      expect(Flag.new.number_of_reviews_for_post).to eq(0)
    end
  end
end
