require "rails_helper"

describe "Topic Reviews" do
  describe "POST /topics/:topic_id/reviews" do
    context "for unauthenticated users" do
      it "redirects to sign in page" do
        topic = create(:topic)
        flag = create(:flag)

        post("/topics/#{topic.id}/reviews", params: { flag_id: flag.id })

        expect(response).to redirect_to(new_user_session_path)
      end
    end

    context "for general users" do
      include_context "authenticated user"

      it "returns forbidden error" do
        topic = create(:topic)
        flag = create(:flag)

        post("/topics/#{topic.id}/reviews", params: { flag_id: flag.id })

        expect(response).to have_http_status(:unauthorized)
      end
    end

    shared_examples "topic flagger" do
      let(:topic) { create(:topic) }
      let(:flag) { create(:flag) }
      let(:flagging) { instance_double(Topics::Flagging) }
      let(:flagging_class) { class_double(Topics::Flagging).as_stubbed_const }

      it "redirects to reviews page w/ success message if created successfully" do
        expect(flagging_class).to receive(:new).with(moderator: current_user,
          topic: topic, flag: flag).and_return(flagging)
        expect(flagging).to receive(:create_review).and_return(true)

        post("/topics/#{topic.id}/reviews", params: { flag_id: flag.id })

        expect(response).to redirect_to(topic_reviews_path(topic))
        expect(flash[:notice]).to be_present
      end

      it "redirects to reviews page w/ error message if flag wasn't created" do
        expect(flagging_class).to receive(:new).with(moderator: current_user,
          topic: topic, flag: flag).and_return(flagging)
        expect(flagging).to receive(:create_review).and_return(false)

        post("/topics/#{topic.id}/reviews", params: { flag_id: flag.id })

        expect(response).to redirect_to(topic_reviews_path(topic))
        expect(flash[:alert]).to be_present
      end
    end

    context "for moderators" do
      include_context "authenticated user" do
        let(:current_user_role) { "moderator" }
      end

      it_behaves_like "topic flagger"
    end

    context "for admins" do
      include_context "authenticated user" do
        let(:current_user_role) { "admin" }
      end

      it_behaves_like "topic flagger"
    end
  end
end
