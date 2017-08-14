RSpec.shared_context "authenticated user" do
  let(:current_user_role) { "member" }
  let(:current_user) { create(:user, role: current_user_role) }

  before do
    sign_in current_user
  end
end
