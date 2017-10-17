require "rails_helper"

describe Posts::Flagging do
  let(:moderator) { instance_double(User) }
  let(:the_post) { instance_double(Post) }
  let(:review_class) { class_double(Review).as_stubbed_const }
  let(:flagging) { Posts::Flagging.new(moderator: moderator, post: the_post, flag: flag) }

  describe "#create_review" do
    context "when flag is general" do
      let(:flag) { instance_double(Flag, resolve?: false) }

      it "creates new review" do
        set_with_resolve_flag = double(destroy_all: true)
        allow(review_class).to receive(:with_resolve_flag).and_return(set_with_resolve_flag)

        expect(review_class).to receive(:create).with(moderator: moderator, post: the_post,
          flag: flag).and_return(true)
        expect(flagging.create_review).to be_truthy
      end

      it "removes review with resolve flag if it exists" do
        set_with_resolve_flag = double
        allow(review_class).to receive(:create)

        expect(review_class).to receive(:with_resolve_flag).with(the_post, moderator)
          .and_return(set_with_resolve_flag)
        expect(set_with_resolve_flag).to receive(:destroy_all)

        flagging.create_review
      end
    end

    context "when flag is resolve" do
      let(:flag) { instance_double(Flag, resolve?: true) }

      it "removes other reviews by this moderator" do
        allow(review_class).to receive(:create)

        set_of_reviews = double
        expect(review_class).to receive(:where).with(post: the_post, moderator: moderator)
          .and_return(set_of_reviews)
        expect(set_of_reviews).to receive(:destroy_all)

        flagging.create_review
      end

      it "creates new review" do
        set_of_reviews = double(destroy_all: true)
        allow(review_class).to receive(:where).and_return(set_of_reviews)

        expect(review_class).to receive(:create).with(moderator: moderator, post: the_post,
          flag: flag).and_return(true)
        expect(flagging.create_review).to be_truthy
      end
    end
  end
end
