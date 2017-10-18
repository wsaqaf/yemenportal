require "rails_helper"

describe "Posts Reviews", type: :request do
  let(:the_post) { create(:post) }

  describe "POST /posts/:post_id/reviews" do
    context "for unauthenticated users" do
      it "redirects to sign in page" do
        the_post = create(:post)
        flag = create(:flag)

        post("/posts/#{the_post.id}/reviews", params: { flag_id: flag.id })

        expect(response).to redirect_to(new_user_session_path)
      end
    end

    context "for members" do
      include_context "authenticated user"

      it "returns forbidden error" do
        the_post = create(:post)
        flag = create(:flag)

        post("/posts/#{the_post.id}/reviews", params: { flag_id: flag.id })

        expect(response).to have_http_status(:unauthorized)
      end
    end

    shared_examples "post flagger" do
      let(:flag) { create(:flag) }
      let(:flagging) { instance_double(Posts::Flagging) }
      let(:flagging_class) { class_double(Posts::Flagging).as_stubbed_const }

      it "redirects to reviews page w/ success message if created successfully" do
        expect(flagging_class).to receive(:new).with(moderator: current_user,
          post: the_post, flag: flag).and_return(flagging)
        expect(flagging).to receive(:create_review).and_return(true)

        post("/posts/#{the_post.id}/reviews", params: { flag_id: flag.id })

        expect(response).to redirect_to(post_reviews_path(the_post))
        expect(flash[:notice]).to be_present
      end

      it "redirects to reviews page w/ error message if flag wasn't created" do
        expect(flagging_class).to receive(:new).with(moderator: current_user,
          post: the_post, flag: flag).and_return(flagging)
        expect(flagging).to receive(:create_review).and_return(false)

        post("/posts/#{the_post.id}/reviews", params: { flag_id: flag.id })

        expect(response).to redirect_to(post_reviews_path(the_post))
        expect(flash[:alert]).to be_present
      end
    end

    context "for moderators" do
      include_context "authenticated user" do
        let(:current_user_role) { "moderator" }
      end

      it_behaves_like "post flagger"
    end

    context "for admins" do
      include_context "authenticated user" do
        let(:current_user_role) { "admin" }
      end

      it_behaves_like "post flagger"
    end
  end

  describe "DELETE /posts/:post_id/reviews/:id" do
    context "for unauthenticated user" do
      it "redirects to sign in page" do
        review = create(:review, post: the_post)

        delete("/posts/#{the_post.id}/reviews/#{review.id}")

        expect(response).to redirect_to(new_user_session_path)
      end
    end

    context "for members" do
      include_context "authenticated user"

      it "returns forbidden error" do
        review = create(:review, post: the_post)

        delete("/posts/#{the_post.id}/reviews/#{review.id}")

        expect(response).to have_http_status(:unauthorized)
      end
    end

    shared_examples "post review remover" do
      it "removes review" do
        review = create(:review, post: the_post, moderator: current_user)

        delete("/posts/#{the_post.id}/reviews/#{review.id}")

        expect(response).to redirect_to(post_reviews_path(the_post))
        expect(flash[:notice]).to be_present
      end

      it "returns an error when user tries to remove other user review" do
        review = create(:review, post: the_post)

        delete("/posts/#{the_post.id}/reviews/#{review.id}")

        expect(response).to have_http_status(:unauthorized)
      end
    end

    context "for moderators" do
      include_context "authenticated user" do
        let(:current_user_role) { "moderator" }
      end

      it_behaves_like "post review remover"
    end

    context "for admins" do
      include_context "authenticated user" do
        let(:current_user_role) { "admin" }
      end

      it_behaves_like "post review remover"
    end
  end
end
