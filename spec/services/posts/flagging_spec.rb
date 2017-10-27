require "rails_helper"

describe Posts::Flagging do
  let(:moderator) { instance_double(User) }
  let(:the_post) { instance_double(Post) }
  let(:flagging) { Posts::Flagging.new(moderator: moderator, post: the_post, flag: flag) }
  let(:review_applier) do
    instance_double(Posts::Flagging::RateApplier, add_rate: true, subtract_rate: true)
  end

  before do
    allow(flagging).to receive(:rate_applier).and_return(review_applier)
  end

  describe "#create_review" do
    context "when flag is general" do
      let(:flag) { instance_double(Flag, resolve?: false, rate: 0) }

      it "creates new review" do
        set_with_resolve_flag = double(destroy_all: true, reviews_rate: 0)
        allow(Review).to receive(:with_resolve_flag).and_return(set_with_resolve_flag)

        expect(Review).to receive(:create).with(moderator: moderator, post: the_post,
          flag: flag).and_return(true)
        expect(review_applier).to receive(:add_rate)
        expect(flagging.create_review).to be_truthy
      end

      it "removes review with resolve flag if it exists" do
        set_with_resolve_flag = double(reviews_rate: 0)
        allow(Review).to receive(:create)

        expect(Review).to receive(:with_resolve_flag).with(the_post, moderator)
          .and_return(set_with_resolve_flag)
        expect(set_with_resolve_flag).to receive(:destroy_all)
        expect(review_applier).to receive(:subtract_rate)

        flagging.create_review
      end
    end

    context "when flag is resolve" do
      let(:flag) { instance_double(Flag, resolve?: true, rate: 0) }

      it "removes other reviews by this moderator" do
        allow(Review).to receive(:create)

        set_of_reviews = double(reviews_rate: 0)
        expect(Review).to receive(:where).with(post: the_post, moderator: moderator)
          .and_return(set_of_reviews)
        expect(set_of_reviews).to receive(:destroy_all)
        expect(review_applier).to receive(:subtract_rate)

        flagging.create_review
      end

      it "creates new review" do
        set_of_reviews = double(destroy_all: true, reviews_rate: 0)
        allow(Review).to receive(:where).and_return(set_of_reviews)

        expect(Review).to receive(:create).with(moderator: moderator, post: the_post,
          flag: flag).and_return(true)
        expect(review_applier).to receive(:add_rate)
        expect(flagging.create_review).to be_truthy
      end
    end
  end
end
