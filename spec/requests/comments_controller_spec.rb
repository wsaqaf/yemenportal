require "rails_helper"

describe CommentsController, type: :request do
  let(:user) { build :user }
  let(:post_obj) { create :post }
  let(:comment) { create :comment, user: user, post: post_obj }

  describe "#index" do
    let(:do_request) { get "/post/#{post_obj.id}/comments" }

    context "success reques" do
      it "return ceccess state" do
        sign_in user
        do_request

        expect(response.status).to eq 200
      end
    end
  end

  describe "#create" do
    let(:params) { { comment: { body: "my comment" } } }
    let(:do_request) { post "/post/#{post_obj.id}/comments", params: params }

    context "success reques" do
      it "return ceccess state" do
        sign_in user
        do_request

        expect(response.status).to eq 200
      end
    end

    context "fail request" do
      let(:params) { { comment: { body: nil } } }

      it "redirect to create form" do
        sign_in user
        do_request

        expect(response.status).to eq 400
      end
    end
  end

  describe "#destroy" do
    let(:do_request) { delete "/post/#{post_obj.id}/comments/#{comment.id}" }

    it "send seccess status" do
      sign_in user
      do_request

      expect(response.status).to eq 200
    end
  end
end
