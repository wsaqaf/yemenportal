require "rails_helper"

describe UsersController, type: :request do
  let(:user) { create :user }

  describe "#edit" do
    let(:do_request) { get "/users/#{user.id}/edit" }

    it "user" do
      sign_in user
      do_request

      expect(response).to be_success
    end
  end

  describe "#update" do
    let(:do_request) do
      put "/users/#{user.id}", params: { user: { first_name: "Max", last_name: "Mad" } }
    end

    it "user params" do
      sign_in user

      do_request
      expect(response).to redirect_to(root_path)
    end
  end
end
